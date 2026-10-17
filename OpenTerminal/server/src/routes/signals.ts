import { Router } from "express";
import { readFile } from "fs/promises";
import path from "path";

export const signalsRouter = Router();

// Path to our signals CSV (relative to server directory)
// Go up three levels from server/ to scratch/, then into trading-platform-demo/signals/
const SIGNALS_CSV_PATH = path.resolve("../../../trading-platform-demo/signals/aapl_ma_signals.csv");

// Helper to parse CSV to array of objects
async function parseCsvToJson(filePath: string): Promise<any[]> {
  try {
    const csv = await readFile(filePath, "utf8");
    const lines = csv.trim().split("\n");
    if (lines.length === 0) return [];
    const headers = lines[0].split(",");
    const result = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(",");
      const obj: any = {};
      for (let j = 0; j < headers.length; j++) {
        // Try to convert numeric values
        const val = values[j];
        const num = Number(val);
        obj[headers[j]] = isNaN(num) ? val : num;
      }
      result.push(obj);
    }

    return result;
  } catch (error) {
    console.error("Error reading signals CSV:", error);
    // Return empty array on error to avoid breaking the UI
    return [];
  }
}

signalsRouter.get("/", async (_req, res) => {
  const data = await parseCsvToJson(SIGNALS_CSV_PATH);
  res.json(data);
});

signalsRouter.get("/latest", async (_req, res) => {
  const data = await parseCsvToJson(SIGNALS_CSV_PATH);
  if (data.length === 0) {
    res.json([]);
    return;
  }
  // Return the latest signal
  const latest = data[data.length - 1];
  res.json(latest);
});