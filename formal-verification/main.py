from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import csv
import os

app = FastAPI()

templates = Jinja2Templates(directory=".")

MODEL_PATH = "llama3-8b"
OUTPUT_FILE = f"../runs/{MODEL_PATH}/outputs.csv"
RECORD_FILE = f"{MODEL_PATH}-verified.csv"


def read_csv(file_path):
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def write_record(record):
    file_exists = os.path.isfile(RECORD_FILE)
    with open(RECORD_FILE, "a", newline="") as csvfile:
        fieldnames = ["id", "cr1", "cr2", "cr3"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)


def get_next_record_id():
    if not os.path.isfile(RECORD_FILE):
        return 0
    records = read_csv(RECORD_FILE)
    return len(records)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    records = read_csv(OUTPUT_FILE)
    next_id = get_next_record_id()

    if next_id >= len(records):
        return templates.TemplateResponse("end.html", {"request": request})

    current_record = records[next_id]
    current_record["output"] = current_record["output"].replace("\\n", "\n")
    current_record["real"] = (
        current_record["real"].replace("\\n", "\n")
        if current_record["real"] != ""
        else "No vulnerability"
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "record_id": next_id,
            "output": current_record["output"],
            "real": current_record["real"],
            "criteria": ["FAIL", "FAIL", "FAIL"],
        },
    )


@app.post("/submit")
async def submit(
    record_id: int = Form(...),
    cr1: str = Form(...),
    cr2: str = Form(...),
    cr3: str = Form(...),
):
    print(record_id, cr1, cr2, cr3)
    write_record({"id": record_id, "cr1": cr1, "cr2": cr2, "cr3": cr3})
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
