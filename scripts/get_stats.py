import pandas as pd
import pickle
from matplotlib import pyplot as plt
from collections import defaultdict

from config import HARBOR_API_URL, HARBOR_ADMIN_USERNAME, HARBOR_ADMIN_PASSWORD
from registry.harbor import Harbor, HarborAPI

api = HarborAPI(HARBOR_API_URL, (HARBOR_ADMIN_USERNAME, HARBOR_ADMIN_PASSWORD))
harbor = Harbor(harbor_api=api)


def count_artifacts():
    record = {}
    for project in api.get_all_projects():
        print(project['name'])
        record[project['name']] = project
        record[project['name']]['repos'] = {}
        for repo in api.get_all_repositories(project['name']):
            record[project['name']]["repos"][repo['name'].split("/")[-1]] = repo
            record[project['name']]["repos"][repo['name'].split("/")[-1]]['artifacts'] = {}
            for artifact in api.get_all_artifacts(project['name'], repo['name'].split("/")[-1]):
                record[project['name']]["repos"][repo['name'].split("/")[-1]]["artifacts"][artifact['id']] = artifact

    pickle.dump(record, open("artifacts.pkl", "wb"))

def artifact_analysis():
    records = pickle.load(open("artifacts.pkl", "rb"))

    total_artifacts = 0
    for project in records.values():
        for repo in project['repos'].values():
            total_artifacts += len(repo['artifacts'])
    print(f"Total artifacts: {total_artifacts}")

    pull_count = 0
    for project in records.values():
        for repo in project['repos'].values():
            pull_count += repo['pull_count']
    print(f"Total pull count: {pull_count}")

    creation_times = []
    for project in records.values():
        for repo in project['repos'].values():
            creation_times += [repo['creation_time']]
    df = pd.DataFrame(creation_times, columns=['creation_time'])
    df["creation_time"] = pd.to_datetime(df["creation_time"])
    df.groupby([df["creation_time"].dt.year, df["creation_time"].dt.month]).count().plot(kind="bar")

    plt.show()
    print(f"Total creation times: {len(creation_times)}")


if __name__ == "__main__":
    artifact_analysis()