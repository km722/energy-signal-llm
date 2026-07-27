from typing import Tuple
import pandas as pd 
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import numpy as np 

EXTRACTIONS_JSON = './data/processed/extractions.json'
GOLD_ENRICHED = './data/labeled/gold_enriched.csv'
GOLD_DATA = './data/labeled/gold.csv'


def process_data(json_path: str = EXTRACTIONS_JSON, gold_labeled_path: str = GOLD_ENRICHED, gold_path: str = GOLD_DATA) -> pd.DataFrame:
    df_gold_enriched = pd.read_csv(gold_labeled_path)
    df_gold = pd.read_csv(gold_path)

    df_gold_enriched['source'] = 'enriched'
    df_gold['source'] = 'random'

    json_df = pd.read_json(json_path).T
    json_df = json_df.reset_index().rename(columns={"index": "webUrl", "event_type": "pred_event", "region": "pred_region"})

    df_all_gold = pd.concat([df_gold,df_gold_enriched], ignore_index = True)

    results = pd.merge(left= df_all_gold, right = json_df, on= 'webUrl', how = 'left').reset_index(drop=True)

    return results

def score(df: pd.DataFrame) -> None:

    for source, group in df.groupby('source'):
        print(f'----Printing Metrics for event_type on dataset {source}----\n')
        acc_event =  accuracy_score(group['event_type'], group['pred_event'])
        cm_event = confusion_matrix(group['event_type'], group['pred_event'])
        report_event = classification_report(group['event_type'], group['pred_event'], zero_division=0)
        baseline_event = group['event_type'].value_counts(normalize=True).max()

        print(f"Baseline {source} : {baseline_event}")
        print(f"Accuracy {source}: {acc_event:.3f} \n" )
        print(f"Confusion Matrix {source}: {cm_event}\n")
        print(f"Classification Report {source}: {report_event}")

    for source, group in df.groupby('source'):
            print(f'----Printing Metrics for region on dataset {source}----')
            acc_region = accuracy_score(group['region'], group['pred_region']) 
            cm_region = confusion_matrix(group['region'], group['pred_region'])
            report_region = classification_report(group['region'], group['pred_region'],zero_division=0)
            baseline_region = group['region'].value_counts(normalize=True).max()

            print(f"Baseline {source} : {baseline_region}")
            print(f"Accuracy {source}: {acc_region:.3f}\n" )
            print(f"Confusion Matrix {cm_region} \n")
            print(f"Classification Report {source}: {report_region}")




if __name__ == "__main__":
    results= process_data()
    print(results.head())
    print(results.shape)
    print(results['pred_event'].notna().all())

    score(results)
    


   
