use good_lp::*;
use std::error::Error;
use std::collections::HashMap;
use std::collections::HashSet;

// Define a function to generate an MPS for maximizing Sharpe ratio
pub fn maximize_sharpe_ratio(
    returns_map: &HashMap<u32, f64>,
    covariance_map: &HashMap<String, f64>,
    max_investment_size: f64,
    min_investment_size: f64,
    max_number_of_stocks: usize,
    max_investment_per_sector: f64,
) -> Result<(), Box<dyn Error>> {
    let mut problem = Problem::new("Maximize_Sharpe_Ratio", Objective::Maximize);

    // Define decision variables for each stock allocation
    let mut allocation_vars = vec![];
    for index in returns_map.keys() {
        let var_name = format!("x{}", index);
        let var = problem.add_var(var_name.as_str(), 0.0, 1.0).unwrap();
        allocation_vars.push(var);
    }

    // Objective function: Maximize Sharpe ratio
    let mut obj_expr: Expression;
    for (i, &var) in allocation_vars.iter().enumerate() {
        for (j, &var_j) in allocation_vars.iter().enumerate() {
            let cov_ij = covariance_map.get(&(i as u32, j as u32)).unwrap_or(&0.0);
            obj_expr += returns_map[&(i as u32)] * var * returns_map[&(j as u32)] * var_j * cov_ij;
        }
    }
    problem.max(obj_expr);

    // Constraints
    // 1. Total investment size constraint
    let total_investment_expr: Expression = allocation_vars.iter().map(|&v| v).sum();
    problem.add_constraint(total_investment_expr <= max_investment_size);

    // 2. Minimum investment size constraint
    for &var in &allocation_vars {
        problem.add_constraint(var >= min_investment_size);
    }

    // 3. Maximum number of stocks constraint
    problem.add_constraint(allocation_vars.iter().map(|&v| v).sum() <= max_number_of_stocks as f64);

    // 4. Maximum investment per sector constraint (assuming sectors are identified)
    // Replace this with actual sector-wise constraints based on your sector lookup

    // Solve the problem
    let solution = problem.solve()?;
    println!("Solution: {:?}", solution);

    Ok(())
}
