import pandas as pd


class CSVAnalyzer:
    """A class for analyzing CSV files using pandas.

    Provides functionalities to load, clean, preprocess,
    analyze, and transform CSV data.
    """

    def __init__(self, csv_file: str):
        """Initializes the CSVAnalyzer with a CSV file.

        Args:
            csv_file (str): Path to the CSV file.
        """
        self.file_path: str = csv_file
        self.df = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """Loads data from the CSV file into a pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing the CSV data.

        Raises:
            FileNotFoundError: If the CSV file is not found.
            pd.errors.ParserError: If there is an issue parsing the CSV file.
            pd.errors.EmptyDataError: If the CSV file is empty.
            Exception: For any other unexpected errors during file loading.
        """
        try:
            df = pd.read_csv(self.file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")
        except pd.errors.ParserError as e:
            error_msg = (
                "Error parsing CSV file: "
                f"{self.file_path}. "
                "Ensure it is a valid CSV format. "
                f"Details: {e}"
            )
            raise pd.errors.ParserError(error_msg)
        except pd.errors.EmptyDataError:
            error_msg = "CSV file is empty or contains no data: " f"{self.file_path}"
            raise pd.errors.EmptyDataError(error_msg)
        except Exception as e:
            error_msg = (
                "Unexpected error loading CSV file: "
                f"{self.file_path}. "
                f"Details: {e}"
            )
            raise Exception(error_msg)

        if df.empty:
            error_msg = "Loaded CSV DataFrame is empty: " f"{self.file_path}"
            raise pd.errors.EmptyDataError(error_msg)
        return df

    def get_head(self, n: int = 5) -> pd.DataFrame:
        """Returns the first n rows of the DataFrame.

        Args:
            n (int, optional): Number of rows to return. Defaults to 5.

        Returns:
            pd.DataFrame: First n rows of the DataFrame.
        """
        return self.df.head(n)

    def get_info(self) -> None:
        """Prints a concise summary of the DataFrame.

        Returns:
            None: This method prints information to standard output.
        """
        self.df.info()
        return None

    def get_description(self) -> pd.DataFrame:
        """Generates descriptive statistics of the DataFrame.

        Returns:
            pd.DataFrame: Descriptive statistics.
        """
        return self.df.describe(include="all")

    def handle_missing_values(
        self, strategy: str = "mean", columns: list[str] | None = None
    ) -> pd.DataFrame:
        """Handles missing values using a specified strategy.

        Args:
            strategy (str, optional): Strategy for handling missing values.
                Options: 'mean', 'median', 'mode', 'drop'. Defaults to 'mean'.
            columns (list[str], optional): Columns to apply the strategy to.
                If None, apply to columns with missing values.

        Returns:
            pd.DataFrame: DataFrame with handled missing values.

        Raises:
            ValueError: If invalid strategy or incompatible column data type.
        """
        valid_strategies = ["mean", "median", "mode", "drop"]
        if strategy not in valid_strategies:
            strategies_str = "', '".join(valid_strategies)
            error_msg = (
                f"Invalid strategy: '{strategy}'. " f"Choose from '{strategies_str}'."
            )
            raise ValueError(error_msg)

        if columns is None:
            columns = self.df.columns[self.df.isnull().any()].tolist()
        if not columns:
            return self.df

        for col in columns:
            if self.df[col].isnull().any():
                is_numeric = pd.api.types.is_numeric_dtype(self.df[col])
                if strategy == "mean" and is_numeric:
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
                elif strategy == "median" and is_numeric:
                    self.df[col].fillna(self.df[col].median(), inplace=True)
                elif strategy == "mode":
                    self.df[col].fillna(self.df[col].mode()[0], inplace=True)
                elif strategy == "drop":
                    self.df.dropna(subset=[col], inplace=True)
                else:
                    error_msg = (
                        f"Strategy '{strategy}' incompatible "
                        f"with column '{col}' type."
                    )
                    raise ValueError(error_msg)
        return self.df

    def remove_duplicates(
        self, columns: list[str] = None, keep: str = "first"
    ) -> pd.DataFrame:
        """Removes duplicate rows from the DataFrame.

        Args:
            columns (list[str], optional): Columns to consider for duplicates.
                If None, all columns are considered.
            keep (str, optional): Which duplicates to keep.
                'first' (default), 'last', or 'drop'.

        Returns:
            pd.DataFrame: DataFrame with duplicate rows removed.
        """
        self.df.drop_duplicates(subset=columns, keep=keep, inplace=True)
        return self.df

    def normalize_data(
        self, columns: list[str] = None, method: str = "min-max"
    ) -> pd.DataFrame:
        """Normalizes numerical data in specified columns.

        Args:
            columns (list[str], optional): Columns to normalize.
                If None, normalize all numerical columns.
            method (str, optional): Normalization method.
                'min-max' (default) or 'z-score'.

        Returns:
            pd.DataFrame: DataFrame with normalized data.

        Raises:
            ValueError: If invalid normalization method provided.
        """
        if columns is None:
            columns = self.df.select_dtypes(include=["number"]).columns.tolist()

        for col in columns:
            if method == "min-max":
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                if min_val != max_val:  # Avoid division by zero
                    self.df[col] = (self.df[col] - min_val) / (max_val - min_val)
            elif method == "z-score":
                mean_val = self.df[col].mean()
                std_val = self.df[col].std()
                if std_val != 0:  # Avoid division by zero
                    self.df[col] = (self.df[col] - mean_val) / std_val
            else:
                raise ValueError(f"Invalid normalization method: {method}")
        return self.df

    def encode_categorical_data(self, columns=None, method="one-hot") -> pd.DataFrame:
        """Encodes categorical data in specified columns.

        Args:
            columns (list, optional): Categorical columns to encode.
                If None, encode all categorical columns.
            method (str): Encoding method ('one-hot').

        Returns:
            pd.DataFrame: DataFrame with encoded categorical data.

        Raises:
            ValueError: If invalid encoding method provided.
        """
        if columns is None:
            columns = self.df.select_dtypes(include=["object"]).columns.tolist()

        if method == "one-hot":
            for col in columns:
                dummies = pd.get_dummies(self.df[col], prefix=col, prefix_sep="_")
                self.df = pd.concat([self.df, dummies], axis=1)
                self.df.drop(columns=[col], inplace=True)
        else:
            raise ValueError(f"Invalid encoding method: {method}")

        return self.df

    def calculate_descriptive_statistics(self, columns=None):
        """
        Calculates descriptive statistics for specified columns.

        Args:
            columns (list, optional): List of columns to calculate statistics for.
                                      If None, calculate for all numerical columns.

        Returns:
            pd.DataFrame: Descriptive statistics.
        """
        if columns is None:
            columns = self.df.select_dtypes(include=["number"]).columns.tolist()
        return self.df[columns].describe()

    def calculate_correlation_matrix(self, method="pearson", columns=None):
        """
        Calculates the correlation matrix for numerical columns.

        Args:
            method (str): Correlation method ('pearson', 'kendall', 'spearman').
            columns (list, optional): List of columns to calculate correlation for.
                                      If None, use all numerical columns.

        Returns:
            pd.DataFrame: Correlation matrix.
        """
        if columns is None:
            columns = self.df.select_dtypes(include=["number"]).columns.tolist()
        return self.df[columns].corr(method=method)

    def analyze_column_distribution(self, column):
        """
        Analyzes the distribution of a single column, providing summary statistics and value counts.

        Args:
            column (str): Name of the column to analyze.

        Returns:
            pd.Series: Value counts (categorical) or descriptive stats (numerical).
        Raises:
            ValueError: If the specified column is not found in the DataFrame.
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")

        if pd.api.types.is_categorical_dtype(
            self.df[column]
        ) or pd.api.types.is_object_dtype(self.df[column]):
            return self.df[column].value_counts()
        elif pd.api.types.is_numeric_dtype(self.df[column]):
            return self.df[column].describe()
        else:
            error_msg = (
                f"Column '{{column}}' is of type {self.df[column].dtype}, "
                "analysis not available."
            )
            return pd.Series(error_msg)

    def detect_outliers(self, column, threshold=3):
        """
        Detects outliers in a numerical column using the Z-score method.

        Args:
            column (str): Name of the column to detect outliers in.
            threshold (int, optional): Z-score threshold for outlier detection. Defaults to 3.

        Returns:
            pd.DataFrame: DataFrame containing rows with outliers in the specified column.
        Raises:
            ValueError: If the specified column is not found or is not numerical.
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")
        if not pd.api.types.is_numeric_dtype(self.df[column]):
            error_msg = (
                f"Column '{column}' is not numerical and cannot be analyzed "
                "for outliers."
            )
            raise ValueError(error_msg)

        z_scores = (self.df[column] - self.df[column].mean()) / self.df[column].std()
        outliers = self.df[abs(z_scores) > threshold]
        return outliers

    def apply_custom_transformation(self, column, func):
        """
        Applies a custom transformation function to a specified column.

        Args:
            column (str): Name of the column to transform.
            func (function): Transformation function to apply to the column.

        Returns:
            pd.DataFrame: DataFrame with the transformed column.
        Raises:
            ValueError: If the specified column is not found.
            TypeError: If the provided function is not callable.
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")
        if not callable(func):
            raise TypeError("Provided transformation is not a callable function.")

        self.df[column] = self.df[column].apply(func)
        return self.df
