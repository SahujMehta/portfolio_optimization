use std::collections::HashMap;
use std::error::Error;
use rand::SeedableRng as _;
use rand::rngs::StdRng;
use serde::de::value;
use tpe::{self, TpeOptimizer};

pub fn maximize_sharpe_ratio(
    returns_map: &HashMap<u32, f64>,
    covariance_map: &HashMap<String, f64>,
    ticker_map: &HashMap<u32, String>,
    sector_lookup: &HashMap<String, Vec<String>>,
    max_investment_size: f64,
    min_investment_size: f64,
    max_number_of_stocks: usize,
    max_investment_per_sector: f64,
    risk_free_rate: f64,
) -> Result<(), Box<dyn Error>> {
    // Define the variables
    let mut optim = TpeOptimizer::new(
        tpe::parzen_estimator(), 
        tpe::range(0.0, 1.0).unwrap() // Use integers for weights
    );

    let objective = |weights: &Vec<f64>| -> f64 {
        // Implement the logic to calculate the Sharpe ratio here
        // You need to calculate portfolio return and standard deviation based on weights
        // And then compute the Sharpe ratio
        // For simplicity, here's a placeholder value
        5.0 
    };

    let mut best_value = std::f64::NEG_INFINITY;
    let mut best_weights = vec![0; returns_map.len()]; // Store the best weights as a vector of integers
    let mut rng = StdRng::from_seed(Default::default());

    for _ in 0..100 {
        let weights: Vec<i32> = optim.ask(&mut rng)?
            .iter()
            .map(|&w| w as i32)
            .collect(); // Convert to integer weights

        let v = objective(&weights);

        optim.tell(weights.clone(), v)?;

        if v > best_value {
            best_value = v;
            best_weights = weights.clone(); // Update best weights
        }

        // Print the weights for each decision variable
        println!("Weights: {:?}", weights);
    }

    // Since we were maximizing the negative Sharpe ratio, the actual Sharpe ratio is negative.
    println!("Best Sharpe Ratio (Negative): {}", -best_value);
    println!("Best Weights: {:?}", best_weights); // Print the best weights

    Ok(())
}
