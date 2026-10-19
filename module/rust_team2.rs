// SPDX-License-Identifier: GPL-2.0-only
//! A small statistics module for the openEuler Rust lifecycle experiment.
// API baseline and upstream sample attribution: ../THIRD_PARTY_NOTICES.md

use kernel::prelude::*;

mod statistics;

use statistics::{summarize, Statistics};

module! {
    type: RustTeam2,
    name: "rust_team2",
    author: "OS Course Task 2 Team",
    description: "Rust statistics and module lifecycle experiment",
    license: "GPL",
}

struct RustTeam2 {
    // The module owns this allocation until its instance is dropped.
    values: Vec<u64>,
    summary: Statistics,
}

impl kernel::Module for RustTeam2 {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        let mut values = Vec::new();
        for value in [3_u64, 1, 4, 1, 5, 9] {
            // Fallible allocation propagates ENOMEM instead of panicking.
            values.try_push(value)?;
        }

        let summary = summarize(&values).map_err(|_| kernel::error::code::EINVAL)?;
        pr_info!(
            "[rust_team2] event=loaded count={} sum={} min={} max={}\n",
            summary.count, summary.sum, summary.min, summary.max
        );
        pr_info!(
            "[rust_team2] event=stats_detail average={} range={}\n",
            summary.average, summary.range
        );
        Ok(Self { values, summary })
    }
}

impl Drop for RustTeam2 {
    fn drop(&mut self) {
        // Fields are dropped AFTER this method. This log is not proof of a
        // completed deallocation or a general absence of memory leaks.
        pr_info!(
            "[rust_team2] event=unload_begin retained={} sum={}\n",
            self.values.len(), self.summary.sum
        );
    }
}
