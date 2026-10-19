// SPDX-License-Identifier: GPL-2.0-only
//! Pure calculation shared by the kernel module and host-side tests.

#[derive(Debug, PartialEq, Eq)]
pub(crate) struct Statistics {
    pub(crate) count: usize,
    pub(crate) sum: u64,
    pub(crate) min: u64,
    pub(crate) max: u64,
    pub(crate) average: u64,
    pub(crate) range: u64,
}

#[derive(Debug, PartialEq, Eq)]
pub(crate) enum StatisticsError {
    EmptyInput,
    SumOverflow,
}

pub(crate) fn summarize(values: &[u64]) -> Result<Statistics, StatisticsError> {
    let first = *values.first().ok_or(StatisticsError::EmptyInput)?;
    let mut result = Statistics {
        count: values.len(),
        sum: 0,
        min: first,
        max: first,
    };
    for &value in values {
        result.sum = result
            .sum
            .checked_add(value)
            .ok_or(StatisticsError::SumOverflow)?;
        result.min = result.min.min(value);
        result.max = result.max.max(value);
    }
    result.average = result.sum / result.count as u64;
    result.range = result.max - result.min;
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn example_has_expected_statistics() {
        assert_eq!(
            summarize(&[3, 1, 4, 1, 5, 9]),
            Ok(Statistics { count: 6, sum: 23, min: 1, max: 9, average: 3, range: 8 })
        );
    }

    #[test]
    fn empty_input_is_rejected() {
        assert_eq!(summarize(&[]), Err(StatisticsError::EmptyInput));
    }

    #[test]
    fn a_single_maximum_value_is_valid() {
        assert_eq!(
            summarize(&[u64::MAX]),
            Ok(Statistics {
                count: 1, sum: u64::MAX, min: u64::MAX, max: u64::MAX,
                average: u64::MAX, range: 0,
            })
        );
    }

    #[test]
    fn addition_overflow_is_reported() {
        assert_eq!(summarize(&[u64::MAX, 1]), Err(StatisticsError::SumOverflow));
    }

    #[test]
    fn repeated_zeroes_are_valid() {
        assert_eq!(
            summarize(&[0, 0, 0]),
            Ok(Statistics {
                count: 3, sum: 0, min: 0, max: 0, average: 0, range: 0,
            })
        );
    }

    #[test]
    fn borrowing_does_not_modify_the_input() {
        let values = [9, 1, 5, 4];
        let result = summarize(&values).unwrap();
        assert_eq!(values, [9, 1, 5, 4]);
        assert_eq!((result.sum, result.min, result.max, result.average, result.range),
                   (19, 1, 9, 4, 8));
    }
}
