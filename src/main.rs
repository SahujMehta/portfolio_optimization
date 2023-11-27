mod source_data;
mod calculations;
mod linear_program;

use calculations::*;
use source_data::*;
use linear_program::*;

use std::error::Error;
use std::collections::{HashSet, HashMap};
use csv::Reader;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let file_path = "S-and-P-500-list.csv"; // Path to your CSV file containing tickers

    // Fetch data for tickers
    let range = "5y";
    let load_data = false;
    if load_data {
        source_data::load_from_list(file_path, range).await?;
    }

    // Determine the risk-free rate based on yield of 13-week Treasury bill, change ticker to change source
    //Until Yahoo Finance fixes, manually look up risk free rate
    //let risk_free_rate = fetch_risk_free_rate("^IRX").await?;
    let risk_free_rate = 0.05;
    println!("\nFetching risk-free rate...{}",risk_free_rate);

    //Calculations from files
    let generate_covariance_lookup = false;
    if generate_covariance_lookup {
        save_covariance_lookup(range)?;
    }

    let covariance_lookup = load_covariance_lookup(range);

    let (unique_tickers, covariance_map) = match covariance_lookup {
        Ok((map, tickers)) => {
            println!("Number of Unique Tickers: {}", tickers.len());
            println!("Number of Covariance Values: {}", map.len());
            (tickers, map)
        },
        Err(err) => {
            eprintln!("Error: {:?}", err);
            (Vec::new(), HashMap::new())
        }
    };
    print_missing_tickers(&unique_tickers, &covariance_map);

    //Calculate the returns for each company
    let returns = calculate_returns(&unique_tickers, range)?;

    //Create a lookup table for the ticker sectors
    let sector_lookup = create_sector_lookup(file_path)?;

    // Print out the sectors and associated tickers (for demonstration)
    // for (sector, tickers) in &sector_lookup {
    //     println!("Sector: {}", sector);
    //     println!("Tickers: {:?}", tickers);
    // }
    let max_investment_size = 0.1;
    let min_investment_size = 0.00;
    let max_number_of_stocks = 30;
    let max_investement_per_sector = 0.3; 

    let mut ticker_map: HashMap<u32, String> = HashMap::new();

    for (index, ticker) in unique_tickers.iter().enumerate() {
        ticker_map.insert(index as u32, ticker.to_string());
    }

    let mut returns_map: HashMap<u32, f64> = HashMap::new();
    for (index, ticker) in ticker_map.iter() {
        returns_map.insert(*index, returns[ticker]);
    }

/////////////////////CALCULATE OPTIMAL PORTFOLIO//////////////////////////

    maximize_sharpe_ratio(
        &returns_map,
        &covariance_map,
        max_investment_size,
        min_investment_size,
        max_number_of_stocks,
        max_investement_per_sector,
    )?;
    
    Ok(())
}