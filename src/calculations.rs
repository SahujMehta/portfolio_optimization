use std::collections::HashMap;
use std::error::Error;
use std::fs;
use std::path::Path;
use csv::Reader;

pub fn calculate_covariance(file_path1: &str, file_path2: &str) -> Result<f64, Box<dyn Error>> {
    // Read CSV files
    let mut reader1 = Reader::from_path(file_path1)?;
    let mut reader2 = Reader::from_path(file_path2)?;

    // Extract closing prices from CSV files
    let mut prices1: Vec<f64> = Vec::new();
    let mut prices2: Vec<f64> = Vec::new();

    for record in reader1.records() {
        let record = record?;
        if let Some(price) = record.get(0).and_then(|s| s.parse::<f64>().ok()) {
            prices1.push(price);
        }
    }

    for record in reader2.records() {
        let record = record?;
        if let Some(price) = record.get(0).and_then(|s| s.parse::<f64>().ok()) {
            prices2.push(price);
        }
    }

    // Calculate covariance
    let len = prices1.len();
    if len != prices2.len() || len == 0 {
        return Err("Invalid data length or empty file".into());
    }

    let mean1: f64 = prices1.iter().sum::<f64>() / len as f64;
    let mean2: f64 = prices2.iter().sum::<f64>() / len as f64;

    let mut covariance = 0.0;
    for i in 0..len {
        covariance += (prices1[i] - mean1) * (prices2[i] - mean2);
    }
    covariance /= len as f64;

    Ok(covariance)
}

pub fn create_covariance_lookup(duration: &str) -> Result<HashMap<String, f64>, Box<dyn Error>> {
    let data_folder = "./data"; // Path to your data folder
    let mut covariance_lookup: HashMap<String, f64> = HashMap::new();

    // Read files in the data folder
    let paths = fs::read_dir(data_folder)?;
    let mut tickers: Vec<String> = Vec::new(); // Store tickers

    for path in paths {
        if let Ok(entry) = path {
            if let Some(file_name) = entry.file_name().to_str() {
                if file_name.ends_with(&format!("{}_Quotes.csv", duration)) {
                    let ticker = file_name.trim_end_matches(&format!("_{}_Quotes.csv", duration));
                    tickers.push(ticker.to_string()); // Store ticker
                }
            }
        }
    }

    // Calculate covariance for every combination of tickers
    for (i, ticker1) in tickers.iter().enumerate() {
        for ticker2 in tickers.iter().skip(i + 1) {
            let file_path1 = format!("{}/{}_{}_Quotes.csv", data_folder, ticker1, duration);
            let file_path2 = format!("{}/{}_{}_Quotes.csv", data_folder, ticker2, duration);

            if let Ok(covariance) = calculate_covariance(&file_path1, &file_path2) {
                covariance_lookup.insert(
                    format!("{}-{}", ticker1, ticker2),
                    covariance,
                );
                covariance_lookup.insert(
                    format!("{}-{}", ticker2, ticker1),
                    covariance, // Assuming covariance is symmetric
                );
            }
        }
    }

    Ok(covariance_lookup)
}
