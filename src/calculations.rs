use std::collections::HashMap;
use std::error::Error;
use std::fs;
use std::path::Path;
use csv::{Reader,ReaderBuilder};

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
    println!("Tickers: {:?}", tickers);
    println!("Number of tickers: {}", tickers.len());

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

pub fn save_covariance_lookup(duration: &str) -> Result<(), Box<dyn Error>> {
    let mut covariance_size = 0;
    let covariance_lookup = create_covariance_lookup(duration)?;

    println!("Covariance Lookup Table:");
    for (key, value) in &covariance_lookup {
        println!("{}: {}", key, value);
        covariance_size += 1;
    }
    println!("Covariance Lookup Table Size: {}", covariance_size);

    let file_name = format!("covariance_lookup_{}.csv", duration);
    let mut csv_data = String::new();

    for (key, value) in &covariance_lookup {
        let line = format!("{},{}\n", key, value);
        csv_data.push_str(&line);
    }

    let folder_path = "data";
    if !Path::new(folder_path).exists() {
        fs::create_dir(folder_path)?;
    }

    // Write to CSV file
    let file_path = format!("{}/{}", folder_path, file_name);
    fs::write(&file_path, csv_data)?;

    println!("Covariance lookup has been saved successfully in file: {}", file_path);
    Ok(())
}


pub fn load_covariance_lookup(duration: &str) -> Result<(HashMap<String, f64>, Vec<String>), Box<dyn Error>> {
    let file_name = format!("covariance_lookup_{}.csv", duration);
    let file_path = format!("data/{}", file_name);

    let mut covariance_lookup: HashMap<String, f64> = HashMap::new();
    let mut unique_tickers: Vec<String> = Vec::new();

    let file = fs::File::open(&file_path)?;
    let mut reader = Reader::from_reader(file);

    for result in reader.records() {
        let record = result?;
        if record.len() >= 2 {
            let ticker_pair = record[0].to_string();
            let value = record[1].parse::<f64>()?;

            // Extract tickers
            let tickers: Vec<&str> = ticker_pair.split('-').collect();
            for ticker in &tickers {
                if !unique_tickers.contains(&ticker.to_string()) {
                    unique_tickers.push(ticker.to_string());
                }
            }

            covariance_lookup.insert(ticker_pair, value);
        }
    }

    Ok((covariance_lookup, unique_tickers))
}

pub fn print_missing_tickers(unique_tickers: &[String], covariance_map: &HashMap<String, f64>) {
    for ticker in unique_tickers {
        let found = covariance_map.keys().any(|key| key.contains(ticker));
        if !found {
            println!("Ticker '{}' is not in the covariance map keys", ticker);
        }
    }
}

pub fn calculate_returns(unique_tickers: &[String], duration: &str) -> Result<HashMap<String, f64>, Box<dyn Error>> {
    let mut total_returns_percentage: HashMap<String, f64> = HashMap::new();

    for ticker in unique_tickers {
        let file_path = format!("data/{}_{}_Quotes.csv", ticker, duration);
        let file = fs::File::open(file_path)?;

        let mut reader = ReaderBuilder::new().has_headers(false).from_reader(file);
        let mut prices: Vec<f64> = Vec::new();

        // Collecting prices from the CSV
        for result in reader.records() {
            let record = result?;
            if let Some(price_str) = record.get(0) {
                let price: f64 = price_str.parse()?;
                prices.push(price);
            }
        }

        if let (Some(initial_price), Some(final_price)) = (prices.first(), prices.last()) {
            // Calculate total return as a percentage
            let total_return_percentage = (*final_price - *initial_price) / *initial_price * 100.0;
            total_returns_percentage.insert(ticker.to_string(), total_return_percentage);
        } else {
            eprintln!("Invalid price data for {}", ticker);
        }
    }

    Ok(total_returns_percentage)
}

