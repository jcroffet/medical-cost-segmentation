const SUMMARY = {
  "meta": {
    "rows_raw": 1338,
    "rows_analysed": 1337,
    "duplicates_removed": 1,
    "columns": [
      "age",
      "sex",
      "bmi",
      "children",
      "smoker",
      "region",
      "charges"
    ],
    "null_count": 0,
    "obesity_cutoff": 30.0,
    "total_spend": 17754185.427659,
    "mean_charges": 13279.121486655948,
    "median_charges": 9386.1613,
    "max_charges": 63770.42801,
    "charges_skew": 1.5153909108403483,
    "smoker_pct": 20.49364248317128,
    "obese_pct": 52.80478683620045
  },
  "segments": [
    {
      "name": "Smoker, BMI 30+",
      "n": 145,
      "mean": 41557.98983986207,
      "median": 40904.1995,
      "total": 6025908.52678,
      "pct_members": 10.845175766641734,
      "pct_spend": 33.94077724000967
    },
    {
      "name": "Non-smoker, BMI 30+",
      "n": 561,
      "mean": 8855.531348680926,
      "median": 8083.9198,
      "total": 4967953.08661,
      "pct_members": 41.95961106955871,
      "pct_spend": 27.981870003849874
    },
    {
      "name": "Non-smoker, BMI <30",
      "n": 502,
      "mean": 7977.029520336653,
      "median": 6761.61525,
      "total": 4004468.819209,
      "pct_members": 37.54674644727001,
      "pct_spend": 22.55506925691163
    },
    {
      "name": "Smoker, BMI <30",
      "n": 129,
      "mean": 21363.217015968992,
      "median": 20167.33603,
      "total": 2755854.99506,
      "pct_members": 9.648466716529544,
      "pct_spend": 15.522283499228815
    }
  ],
  "concentration": {
    "top_5pct": 17.34550224620504,
    "top_10pct": 31.789152406099348,
    "top_20pct": 51.57611062332697,
    "top_50pct": 81.41951601153255
  },
  "bmi_bands": [
    {
      "band": "<25",
      "n_non_smoker": 190,
      "n_smoker": 55,
      "mean_non_smoker": 7515.708890789474,
      "mean_smoker": 19839.278308545454
    },
    {
      "band": "25-30",
      "n_non_smoker": 312,
      "n_smoker": 74,
      "mean_non_smoker": 8257.961954996794,
      "mean_smoker": 22495.87416337838
    },
    {
      "band": "30-35",
      "n_non_smoker": 316,
      "n_smoker": 74,
      "mean_non_smoker": 8553.954037879746,
      "mean_smoker": 39640.59289297297
    },
    {
      "band": "35-40",
      "n_non_smoker": 175,
      "n_smoker": 50,
      "mean_non_smoker": 9670.440599828571,
      "mean_smoker": 42753.6228728
    },
    {
      "band": "40+",
      "n_non_smoker": 70,
      "n_smoker": 21,
      "mean_non_smoker": 8179.664366714285,
      "mean_smoker": 45467.786145714286
    }
  ],
  "age_bands": [
    {
      "band": "18-29",
      "n_non_smoker": 330,
      "n_smoker": 86,
      "mean_non_smoker": 4426.9895017242425,
      "mean_smoker": 27518.035261860463,
      "gap": 23091.04576013622
    },
    {
      "band": "30-39",
      "n_non_smoker": 199,
      "n_smoker": 58,
      "mean_non_smoker": 6337.36294517588,
      "mean_smoker": 30271.246414999998,
      "gap": 23933.88346982412
    },
    {
      "band": "40-49",
      "n_non_smoker": 217,
      "n_smoker": 62,
      "mean_non_smoker": 9183.34209718894,
      "mean_smoker": 32654.718697258064,
      "gap": 23471.376600069125
    },
    {
      "band": "50-64",
      "n_non_smoker": 317,
      "n_smoker": 68,
      "mean_non_smoker": 13430.898766782335,
      "mean_smoker": 38748.347617941174,
      "gap": 25317.44885115884
    }
  ],
  "bmi_slopes": {
    "smoker": {
      "slope_below": 490.5443609290708,
      "slope_above": 544.8745273841889,
      "step_at_cutoff": 20194.77282389308,
      "n_below": 129,
      "n_above": 145
    },
    "non_smoker": {
      "slope_below": 184.38683540718174,
      "slope_above": 8.031322415478934,
      "step_at_cutoff": 878.501828344275,
      "n_below": 502,
      "n_above": 561
    }
  },
  "regions": [
    {
      "region": "northeast",
      "n": 324,
      "smoker_pct": 20.679012345679013,
      "obese_pct": 44.135802469135804,
      "mean_bmi": 29.173503086419753,
      "mean_charges": 13406.384516385804,
      "obese_smoker_pct": 8.950617283950617
    },
    {
      "region": "northwest",
      "n": 324,
      "smoker_pct": 17.901234567901234,
      "obese_pct": 45.370370370370374,
      "mean_bmi": 29.195493827160494,
      "mean_charges": 12450.840843950617,
      "obese_smoker_pct": 7.098765432098765
    },
    {
      "region": "southeast",
      "n": 364,
      "smoker_pct": 25.0,
      "obese_pct": 66.75824175824175,
      "mean_bmi": 33.35598901098901,
      "mean_charges": 14735.41143760989,
      "obese_smoker_pct": 15.934065934065933
    },
    {
      "region": "southwest",
      "n": 325,
      "smoker_pct": 17.846153846153847,
      "obese_pct": 53.230769230769226,
      "mean_bmi": 30.596615384615383,
      "mean_charges": 12346.937377292308,
      "obese_smoker_pct": 10.76923076923077
    }
  ],
  "levers": [
    {
      "lever": "Smoking cessation - obese smokers",
      "n": 145,
      "current_spend": 6025908.52678,
      "ceiling_saving": 4741856.481221265,
      "ceiling_pct_of_book": 26.708386597303374,
      "per_head": 32702.45849118114,
      "at_5pct": 237092.82406106326,
      "at_10pct": 474185.6481221265,
      "at_20pct": 948371.296244253,
      "confidence": "High",
      "effort": "Medium"
    },
    {
      "lever": "Smoking cessation - non-obese smokers",
      "n": 129,
      "current_spend": 2755854.99506,
      "ceiling_saving": 1726818.1869365717,
      "ceiling_pct_of_book": 9.726259726038377,
      "per_head": 13386.187495632339,
      "at_5pct": 86340.90934682859,
      "at_10pct": 172681.81869365717,
      "at_20pct": 345363.63738731435,
      "confidence": "High",
      "effort": "Medium"
    },
    {
      "lever": "Weight programme - obese smokers",
      "n": 145,
      "current_spend": 6025908.52678,
      "ceiling_saving": 2928242.059464496,
      "ceiling_pct_of_book": 16.493249275760228,
      "per_head": 20194.772823893076,
      "at_5pct": 146412.1029732248,
      "at_10pct": 292824.2059464496,
      "at_20pct": 585648.4118928992,
      "confidence": "Low",
      "effort": "High"
    },
    {
      "lever": "Weight programme - obese non-smokers",
      "n": 561,
      "current_spend": 4967953.086610001,
      "ceiling_saving": 492839.5257011382,
      "ceiling_pct_of_book": 2.775906152998438,
      "per_head": 878.5018283442748,
      "at_5pct": 24641.97628505691,
      "at_10pct": 49283.95257011382,
      "at_20pct": 98567.90514022764,
      "confidence": "Medium",
      "effort": "High"
    }
  ],
  "unexplained": {
    "high_cost_non_smokers": 10,
    "non_smoker_total": 1063,
    "their_spend": 326626.49775000004,
    "pct_of_book": 1.8397154805038427
  }
};
