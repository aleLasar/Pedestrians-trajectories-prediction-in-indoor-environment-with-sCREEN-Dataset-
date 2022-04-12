import pandas as pd
from st_dbscan import ST_DBSCAN

class Refained_Data:

    __data = None

    def __init__(self, PATH):
        data = pd.read_csv(PATH)
        data['time'] = pd.to_datetime(data['time'], format='%Y-%m-%d %H:%M:%S.%f')
        data = data.set_index("id")
        data = data.drop(columns=['z'])
        data = data.sort_values('time')
        self.__data = data

    def get_dataset(self):
        return self.__data
    
    def read_trajectories(self, PATH):
        """
        Return all the trajectories from a csv file
        :PATH:
        :return: list of DataFrame; every cell is a trajectory
        """
        data = pd.read_csv(PATH, header = 0)
        data['time'] = pd.to_datetime(data['time'], format='%Y-%m-%d %H:%M:%S')
        position = data.ne(data.shift()).filter(like='n_traj').apply(lambda x: x.index[x].tolist())
        position = position["n_traj"].tolist()
        position += [len(data)]

        trajectories = []
        for i in range(len(position)-1):
            start = position[i]
            end  = position[i + 1]
            traj = data.iloc[start:end]
            traj.set_index(pd.Index(range(0, len(traj))), drop=True, inplace=True)
            trajectories.append(traj)

        return trajectories

    def __euclidea (self,x1,y1,x2,y2):
        return pow((pow(x2-x1,2)+pow(y2-y1,2)),0.5)

    def split_4_dataMissing(self, df):
        """
        Approach based on data missing in the dataset: the trajectories are detected if between two point there is a gap of 5m
        :param df: Single DataFrame with dataTime collum with name "time"
        :return: list of DataFrame; every cell is a trajectory
        """
        all_trajectories = []

        previous_time = df['time'].iloc[0]
        start = 0

        for idx in range(len(df)):
            row = df.iloc[idx]
            current_time = row['time']
            time_delta = current_time - previous_time
            minutes_delta = time_delta.total_seconds()//60
            if minutes_delta >= 5:
                end = idx
                current_traj = df.iloc[start:end]
                all_trajectories.append(current_traj)
                start = idx

            previous_time = current_time
        all_trajectories.append(df.iloc[start:len(df) - 1])
        return all_trajectories

    def remove_dense_trajectories(self, list_trajectories, threshold):
        """
        Remove all the trajectories that have a Standard Deviation smaller than a Threshold

        :param list_trajectories: List of DataFrame. Required two collums with names "x" and "y"
        :param threshold: Integer/Float
        :return: List of DataFrame; every cell is a trajectory
        """
        trajectories = []
        for idx, row in enumerate(list_trajectories):
            std_x = row["x"].std()
            std_y = row["y"].std()
            if std_x > threshold or std_y > threshold:
                trajectories.append(row)
        return trajectories
    
    def remove_shorter(self, array, thrs):
        return [x for x in array if len(x) >= thrs]



    def get_std_time_array(self, array):
        """
        :param array: List od dataframe (every dataframe is a trajectory)
        :return: List of array: Every cell contain: std_x, std_y and time for the current trajectory
        """
        result = []
        for idx, traj in enumerate(array):
            delta_time = traj['time'].max() - traj['time'].min()
            delta_time = delta_time.seconds
            std_x = traj["x"].std()
            std_y = traj["y"].std()
            result.append([std_x, std_y, delta_time])
        return result

    def remove_cluster_point(self, list_trajectories, thrs_1, thrs_2):
        """
        With ST-DBSCAN remove cluster of point inside the trajectory

        :param list_trajectories: List of DataFrame. Every element is a trajectory
        :param thrs_1: Integer/Float Spatial Treshold for ST-DBSCAN (Euclidean distance)
        :param thrs_2: Integer/Float Time Treshold for ST-DBSCAN (sec)
        :return: List of DataFrame; every cell is a trajectory
        """
        return_trajectories = []
        for idx, traj in enumerate(list_trajectories):
            sub_traj = pd.DataFrame()
            #sub_traj = traj[["time", "x", "y"]]
            #sub_traj["time"] = sub_traj[['time']].apply(lambda x: x[0].timestamp(), axis=1).astype(int)
            sub_traj["time"] = traj[['time']].apply(lambda x: x[0].timestamp(), axis=1).astype(int)

            sub_traj.insert(1, "x", traj["x"])
            sub_traj.insert(2, "y", traj["y"])

            st_dbscan = ST_DBSCAN(eps1=thrs_1, eps2=thrs_2, min_samples=100)
            st_dbscan.fit(sub_traj)
            labels = st_dbscan.labels
            traj.insert(4, "label", labels)
            traj = traj.loc[traj["label"] == -1]
            traj_to_add = traj.drop(columns = "label")
            return_trajectories.append(traj_to_add)

        return return_trajectories

    def find_trajectory(self, df, thrs_1, thrs_2, thrs_3, thrs_4):
        """
        Chain of method to get a refained trajectory 

        :param df: DataFrame with dataTime collum with name "time"
        :param thrs_1: Integer/Float, Standard deviation threshold
        :param thrs_2: Integer, Minimun number of points in a trajectory
        :param thrs_3: Integer, Spatian Treshold for ST-DBSCAN
        :param thrs_4: Integer, Time Treshold for ST-DBSCAN
        :return:Trajectories: list of DataFrame; every cell is a trajectory
        """
        trajectories = []
        sub_traj = self.split_4_dataMissing(df)
        sub_traj = self.remove_shorter(sub_traj, thrs_2)
        sub_traj = self.remove_dense_trajectories(sub_traj, thrs_1)

        out_of_cluster = self.remove_cluster_point(sub_traj, thrs_3, thrs_4)

        for idx, traj in enumerate(out_of_cluster):
            clear_traj = self.split_4_dataMissing(traj)
            clear_traj = self.remove_shorter(clear_traj, thrs_2)
            clear_traj = self.remove_dense_trajectories(clear_traj, thrs_1)
            trajectories += clear_traj

        return trajectories