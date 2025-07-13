use wasm_bindgen::prelude::*;

use serde::{Deserialize, Serialize};

use nucleo_matcher::{Config, Matcher, Utf32String, pattern::Pattern};

const ACM_1998: &str = include_str!("../../extractor/acm_classification_1998.json");
const ACM_2012: &str = include_str!("../../extractor/acm_classification_2012.json");
const MSC_2010: &str = include_str!("../../extractor/acm_msc_2010.json");

#[derive(Serialize, Deserialize)]
pub struct Classification {
    pub name: String,
    pub url: String,
    pub codes: Vec<ClassificationCode>,
}

#[wasm_bindgen]
#[derive(Serialize, Deserialize, Clone)]
pub struct ClassificationCode {
    code: String,
    desc: String,
    ancestor_codes: Vec<String>,
    ancestor_descs: Vec<String>,
}

#[wasm_bindgen]
pub struct FuzzySeach {
    matcher: Matcher,
    query: Pattern,
    codes: Vec<ClassificationCode>,
    hayst: Vec<Utf32String>,
}

#[wasm_bindgen]
pub fn search(fz: &mut FuzzySeach, query: &str) -> Vec<JsValue> {
    fz.query.reparse(
        query,
        nucleo_matcher::pattern::CaseMatching::Ignore,
        nucleo_matcher::pattern::Normalization::Smart,
    );

    let mut top_10_matches: Vec<(usize, u32)> = Vec::new();
    for (i, text) in fz.hayst.iter().enumerate() {
        let score = fz.query.score(text.slice(..), &mut fz.matcher);

        if let Some(score_u32) = score {
            if top_10_matches.len() < 10 {
                top_10_matches.push((i, score_u32));
            } else {
                if let Some((min_pos, (_, min_value))) = top_10_matches
                    .iter()
                    .enumerate()
                    .min_by_key(|(_, (_, score))| *score)
                {
                    if *min_value < score_u32 {
                        top_10_matches[min_pos] = (i, score_u32);
                    }
                }
            }
        }
    }

    top_10_matches.sort_by_key(|(_, score)| *score);

    let matches: Vec<JsValue> = top_10_matches
        .iter()
        .map(|(index, _)| {
            let code = &fz.codes[*index];
            serde_wasm_bindgen::to_value(&code).unwrap()
        })
        .collect();

    matches
}

fn create_fz_for_dataset(s: &str) -> FuzzySeach {
    let classification: Classification = serde_json::from_str(s).unwrap();
    let mut codes = Vec::new();
    let mut hayst = Vec::new();
    let matcher = Matcher::new(Config::DEFAULT);
    let query = Pattern::default();

    for code in classification.codes {
        let ancestors = code.ancestor_codes.join(" > ");
        let haystack = Utf32String::from(format!("{} : {} | {}", code.code, ancestors, code.desc));
        codes.push(code);
        hayst.push(haystack);
    }

    FuzzySeach {
        matcher,
        query,
        codes,
        hayst,
    }
}

#[wasm_bindgen]
pub fn new_fuzzy_search() -> Box<[FuzzySeach]> {
    let acm_1998 = create_fz_for_dataset(ACM_1998);
    let acm_2012 = create_fz_for_dataset(ACM_2012);
    let msc_2010 = create_fz_for_dataset(MSC_2010);

    Box::new([acm_1998, acm_2012, msc_2010])
}
