use yahoo_finance_api as yahoo;
use std::error::Error;
use std::fs::File;
use std::path::Path;
use std::time::Duration;
use std::io::prelude::*;
use tokio;
use csv;

pub async fn load_from_list(range: &str ) -> Result<(), Box<dyn std::error::Error>> {
    let file_path = "S-and-P-500-list.csv"; // Path to your CSV file containing tickers

    let file = std::fs::File::open(file_path)?;
    let mut rdr = csv::Reader::from_reader(file);

    // Process tickers
    println!("\nFetching data for tickers:");
    let mut counter = 0;
    let mut error_counter = 0;
    for result in rdr.records() {
        let record = result?;
        if counter % 3 == 0 { // Fetch data for every third item
            if let Some(ticker) = record.get(0) {
                println!("Fetching data for {}", ticker);
                if let Err(err) = fetch_and_store_data(ticker, range).await {
                    eprintln!("Error fetching data for {}: {}", ticker, err);
                    error_counter += 1;
                }
            }
        }
        counter += 1;
    }
    println!("Attempted to fetch and store data for {} tickers, {} tickers failed", counter, error_counter);
    Ok(())
}


pub async fn fetch_and_store_data(ticker: &str, range: &str) -> Result<(), Box<dyn Error>> {
    let interval = "1d";
    let provider = yahoo::YahooConnector::new();
    let response = provider.get_quote_range(ticker, interval, range).await?;
    let quotes = response.quotes()?;
    
    // Prepare CSV data
    let mut csv_data = String::new();
    for quote in quotes {
        let line = format!("{}\n", quote.close);
        csv_data.push_str(&line);
    }

    let folder_path = "data";
    if !Path::new(folder_path).exists() {
        std::fs::create_dir(folder_path)?;
    }

    // Write to CSV file
    let file_name = format!("{}/{}_{}_Quotes.csv", folder_path, ticker, range);
    let mut file = File::create(&file_name)?;
    file.write_all(csv_data.as_bytes())?;

    println!("Data has been fetched and stored successfully in file: {}", file_name);
    Ok(())
}

pub async fn fetch_risk_free_rate(ticker: &str) -> Result<f64, Box<dyn Error>> {
    let interval = "1d";
    let provider = yahoo::YahooConnector::new();
    let response = provider.get_quote_range(ticker, interval, "1d").await?;
    let quotes = response.quotes()?;
    
    if let Some(quote) = quotes.first() {
        let close_price = quote.close / 100.0;
        return Ok(close_price);
    }

    Err("No quotes found".into())
}

