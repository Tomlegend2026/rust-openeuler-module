// SPDX-License-Identifier: GPL-2.0-only
//! User-space teaching example, NOT a kernel module.
#[path = "../../../module/statistics.rs"]
mod statistics;

struct OwnedDataset {
    values: Vec<u64>,
}

impl Drop for OwnedDataset {
    fn drop(&mut self) {
        println!("Drop begins: {} elements; the Vec field is dropped afterwards.", self.values.len());
    }
}

fn main() {
    println!("User-space ownership demo; no kernel module is loaded.");
    {
        let values = vec![3, 1, 4, 1, 5, 9];
        let dataset = OwnedDataset { values };
        let result = statistics::summarize(&dataset.values).expect("fixed input is valid");
        println!("Borrowed summary: {:?}", result);
        println!("The owner still holds: {:?}", dataset.values);
    }
    println!("Scope ended; the dataset and its Vec have been dropped.");
}
