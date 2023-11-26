mod source_data;
mod calculations;

use calculations::*;
use source_data::*;
use std::error::Error;


#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Fetch data for tickers
    let range = "5y";
    let load_data = false;
    if load_data {
        source_data::load_from_list(range).await?;
    }

    // Determine the risk-free rate based on yield of 13-week Treasury bill, change ticker to change source
    let risk_free_rate = fetch_risk_free_rate("^IRX").await?;
    println!("\nFetching risk-free rate...{}",risk_free_rate);

    //Calculations from files
    let mut covariance_size = 0;
    if let Ok(covariance_lookup) = create_covariance_lookup(range) {
        println!("Covariance Lookup Table:");
        for (key, value) in covariance_lookup {
            println!("{}: {}", key, value);
            covariance_size += 1;
        }
        println!("Covariance Lookup Table Size: {}", covariance_size);
    } else {
        println!("Error creating covariance lookup.");
    }



    Ok(())

}