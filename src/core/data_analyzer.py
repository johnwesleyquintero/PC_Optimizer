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
            pd.errors.ParserError: If there is an issue parsing the CSV file (e.g., invalid CSV format).
            pd.errors.EmptyDataError: If the CSV file is empty or contains no data.
            Exception: For any other unexpected errors during file loading.
        """
        try:
            df = pd.read_csv(self.file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")
        except pd.errors.ParserError as e:
            raise pd.errors.ParserError(f"Error parsing CSV file: {self.file_path}. Ensure it is a valid CSV format. Details: {e}")
        except pd.errors.EmptyDataError:
            raise pd.errors.EmptyDataError(f"CSV file is empty or contains no data: {self.file_path}")
        except Exception as e:
            raise Exception(f"Unexpected error loading CSV file: {self.file_path}. Details: {e}")

        if df.empty:
            raise pd.errors.EmptyDataError(f"Loaded CSV DataFrame is empty: {self.file_path}")
        return df

    def get_head(self, n: int = 5) -> pd.DataFrame:
        """
        Returns the first n rows of the DataFrame.

        Args:
            n (int, optional): Number of rows to return. Defaults to 5.

        Returns:
            pd.DataFrame: First n rows of the DataFrame.
        """
        return self.df.head(n)

    def get_info(self) -> None:
        """
        Prints a concise summary of the DataFrame, including column names,
        non-null values and memory usage.

        Returns:
            None: This method prints information to standard output and returns None.
        """
        self.df.info()
        return None

    def get_description(self) -> pd.DataFrame:
        """
        Generates descriptive statistics of the DataFrame.

        Returns:
            pd.DataFrame: Descriptive statistics of the DataFrame, including count, mean, std, min, max, and percentiles.
        """
        return self.df.describe(include='all')

    def handle_missing_values(
        self, strategy: str = 'mean', columns: list[str] | None = None
    ) -> pd.DataFrame:
        """Handles missing values in the DataFrame using a specified strategy for specified columns.

        Args:
            strategy (str, optional): Strategy for handling missing values.
                Options are 'mean', 'median', 'mode', 'drop'. Defaults to 'mean'.
            columns (list[str], optional): List of column names to apply the missing value strategy to.
                If None, apply strategy to columns with missing values. Defaults to None.

        Returns:
            pd.DataFrame: DataFrame with handled missing values.

        Raises:
            ValueError: If invalid strategy or incompatible column data type.
        """
        if strategy not in ['mean', 'median', 'mode', 'drop']:
            raise ValueError(f"Invalid strategy: '{strategy}'. Choose from 'mean', 'median', 'mode', 'drop'.")

        if columns is None:
            columns = self.df.columns[self.df.isnull().any()].tolist()
        if not columns:
            return self.df

        for col in columns:
            if self.df[col].isnull().any():
                if strategy == 'mean' and pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
                elif strategy == 'median' and pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col].fillna(self.df[col].median(), inplace=True)
                elif strategy == 'mode':
                    self.df[col].fillna(self.df[col].mode()[0], inplace=True)
                elif strategy == 'drop':
                    self.df.dropna(subset=[col], inplace=True)
                else:
                    raise ValueError(f"Strategy '{strategy}' incompatible with column '{col}' type.")
        return self.df

    def remove_duplicates(self, columns: list[str] = None, keep: str = 'first') -> pd.DataFrame:
        """
        Removes duplicate rows from the DataFrame based on specified columns.

        Args:
            columns (list[str], optional): List of column names to consider when identifying duplicate rows.
                                      If None, all columns are considered. Defaults to None.
            keep (str, optional): Determines which duplicates to keep.
                - 'first': (default) Drop duplicates except for the first occurrence.
                - 'last': Drop duplicates except for the last occurrence.
                - 'drop': Drop all duplicates.
                Defaults to 'first'.

        Returns:
            pd.DataFrame: DataFrame with duplicate rows removed.
        """
        self.df.drop_duplicates(subset=columns, keep=keep, inplace=True)
        return self.df

    def normalize_data(self, columns: list[str] = None, method: str = 'min-max') -> pd.DataFrame:
        """
        Normalizes numerical data in specified columns using the chosen method.

        Args:
            columns (list[str], optional): List of column names to normalize.
                If None, normalization is applied to all numerical columns. Defaults to None.
            method (str, optional): Normalization method to use.
                - 'min-max': (default) Min-Max scaling.
                - 'z-score': Z-score standardization.
                Defaults to 'min-max'.

        Returns:
            pd.DataFrame: DataFrame with normalized numerical data.

        Raises:
            ValueError: If an invalid normalization method is provided.
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['number']).columns.tolist()

        for col in columns:
            if method == 'min-max':
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                if min_val != max_val:  # Avoid division by zero
                    self.df[col] = (self.df[col] - min_val) / (max_val - min_val)
            elif method == 'z-score':
                mean_val = self.df[col].mean()
                std_val = self.df[col].std()
                if std_val != 0:  # Avoid division by zero
                    self.df[col] = (self.df[col] - mean_val) / std_val
            else:
                raise ValueError(f"Invalid normalization method: {method}")
        return self.df

    def encode_categorical_data(self, columns=None, method='one-hot'):
        """
        Encodes categorical data in specified columns.

        Args:
            columns (list, optional): List of categorical columns to encode. If None, encode all categorical columns.
            method (str): Encoding method ('one-hot').

        Returns:
            pd.DataFrame: DataFrame with encoded categorical data.
        Raises:
            ValueError: If an invalid encoding method is provided.
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['object', 'category']).columns.tolist()

        for col in columns:
            if method == 'one-hot':
                self.df = pd.get_dummies(self.df, columns=[col], prefix=[col], dummy_na=False)  # dummy_na=False to exclude NaN category
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
            columns = self.df.select_dtypes(include=['number']).columns.tolist()
        return self.df[columns].describe()

    def calculate_correlation_matrix(self, method='pearson', columns=None):
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
            columns = self.df.select_dtypes(include=['number']).columns.tolist()
        return self.df[columns].corr(method=method)

    def analyze_column_distribution(self, column):
        """
        Analyzes the distribution of a single column, providing summary statistics and value counts.

        Args:
            column (str): Name of the column to analyze.

        Returns:
            pd.Series: Value counts for categorical columns or descriptive statistics for numerical columns.
        Raises:
            ValueError: If the specified column is not found in the DataFrame.
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")

        if pd.api.types.is_categorical_dtype(self.df[column]) or \
           pd.api.types.is_object_dtype(self.df[column]):
            return self.df[column].value_counts()
        elif pd.api.types.is_numeric_dtype(self.df[column]):
            return self.df[column].describe()
        else:
            return pd.Series(f"Column '{column}' is of type {self.df[column].dtype}, analysis not available.")

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
            raise ValueError(f"Column '{column}' is not numerical and cannot be analyzed for outliers.")

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
