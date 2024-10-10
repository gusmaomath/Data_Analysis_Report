# %%
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO


def generate_html_analysis(df, output_html="output.html", max_categories=10):
    """
    Generates an HTML file with statistical analysis, charts for each column, and correlation analysis for numerical variables.

    Args:
        df (pd.DataFrame): The DataFrame to be analyzed.
        output_html (str): The name of the HTML file to be generated. Default is 'output.html'.
        max_categories (int): The maximum number of categories to display in bar charts. Default is 10.
    """

    # General settings for the plots
    sns.set_theme(style="whitegrid", palette="deep", context="notebook")

    # Start the HTML content with general information at the top
    shape_info = df.shape
    column_names = df.columns.tolist()
    num_duplicated_lines = df.duplicated().sum()
    num_missing_values = df.isna().sum().sum()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Analysis Report</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="container pt-4">
        <h1>Data Analysis Report</h1>
        <h2>General Information</h2>
        <p><strong>Shape:</strong> {shape_info[0]} rows, {shape_info[1]} columns</p>
        <p><strong>Column Names:</strong> {', '.join(column_names)}</p>
        <p><strong>Number of duplicated lines:</strong> {num_duplicated_lines}</p>
        <p><strong>Number of missing values (NaN/Null):</strong> {num_missing_values}</p>

        <ul class="nav nav-tabs" id="myTab" role="tablist">
    """

    tab_content = '<div class="tab-content" id="myTabContent">'

    # Generate statistics and charts for each column
    for i, column in enumerate(df.columns):
        active_class = "active" if i == 0 else ""
        show_class = "show" if i == 0 else ""
        aria_selected = "true" if i == 0 else "false"

        # Add a tab for each column
        html_content += f"""
        <li class="nav-item" role="presentation">
            <button class="nav-link {active_class}" id="{column}-tab" data-bs-toggle="tab" data-bs-target="#{column}" type="button" role="tab" aria-controls="{column}" aria-selected="{aria_selected}">{column}</button>
        </li>
        """

        # Add the content for the statistics and charts in the tab
        tab_content += f"""
        <div class="tab-pane fade {show_class}" id="{column}" role="tabpanel" aria-labelledby="{column}-tab">
            <h2>Analysis for column: {column}</h2>
        """

        # Get the statistics for the column
        stats = df[column].describe(include="all")

        # Add the statistics to the HTML, checking if the column is numeric or categorical
        if pd.api.types.is_numeric_dtype(df[column]):
            tab_content += f"""
            <p><strong>Count:</strong> {stats.get('count', 'N/A')}</p>
            <p><strong>Mean:</strong> {stats.get('mean', 'N/A')}</p>
            <p><strong>Standard Deviation:</strong> {stats.get('std', 'N/A')}</p>
            <p><strong>Min:</strong> {stats.get('min', 'N/A')}</p>
            <p><strong>25%:</strong> {stats.get('25%', 'N/A')}</p>
            <p><strong>Median:</strong> {stats.get('50%', 'N/A')}</p>
            <p><strong>75%:</strong> {stats.get('75%', 'N/A')}</p>
            <p><strong>Max:</strong> {stats.get('max', 'N/A')}</p>
            """

            # Generate the histogram for numeric columns
            plt.figure(figsize=(10, 6))
            sns.histplot(df[column].dropna(), bins=20, color="blue", kde=True)
            plt.title(f"Histogram of {column}")
            plt.xlabel(column)
            plt.ylabel("Frequency")
        else:
            # For categorical columns, show relevant statistics
            tab_content += f"""
            <p><strong>Count:</strong> {stats.get('count', 'N/A')}</p>
            <p><strong>Unique:</strong> {stats.get('unique', 'N/A')}</p>
            <p><strong>Top:</strong> {stats.get('top', 'N/A')}</p>
            <p><strong>Frequency of Top:</strong> {stats.get('freq', 'N/A')}</p>
            """

            # Filter the data for categorical columns to show only the top 'max_categories' categories
            value_counts = df[column].value_counts().head(max_categories)
            filtered_data = df[df[column].isin(value_counts.index)]

            # Generate the bar chart for categorical columns
            plt.figure(figsize=(10, 6))
            sns.countplot(
                x=column,
                data=filtered_data,
                order=value_counts.index,
                hue=column,
                dodge=False,
                palette="viridis",
                legend=False,
            )
            plt.title(f"Bar Chart of {column} (Top {max_categories} categories)")
            plt.xlabel(column)
            plt.ylabel("Frequency")
            plt.xticks(
                rotation=90
            )  # Rotate the x-axis labels by 90 degrees for better readability

        # Save the plot as a base64-encoded image
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight", facecolor="w")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plt.close()

        # Add the image to the tab content
        tab_content += (
            f'<img src="data:image/png;base64,{image_base64}" class="img-fluid" />'
        )
        tab_content += "</div>"

    # Add a tab for correlation analysis
    html_content += """
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="correlation-tab" data-bs-toggle="tab" data-bs-target="#correlation" type="button" role="tab" aria-controls="correlation" aria-selected="false">Correlation Analysis</button>
    </li>
    """
    tab_content += """
    <div class="tab-pane fade" id="correlation" role="tabpanel" aria-labelledby="correlation-tab">
        <h2>Correlation Analysis</h2>
    """

    # Generate the correlation heatmap for numeric columns
    numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns
    if len(numeric_columns) > 1:
        plt.figure(figsize=(12, 8))
        correlation_matrix = df[numeric_columns].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
        plt.title("Correlation Heatmap")

        # Save the heatmap as a base64-encoded image
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight", facecolor="w")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plt.close()

        # Add the heatmap to the tab content
        tab_content += (
            f'<img src="data:image/png;base64,{image_base64}" class="img-fluid" />'
        )

    tab_content += "</div>"  # Close the correlation tab content
    tab_content += "</div>"  # Close the tab content wrapper

    # Finish the HTML with the footer
    html_content += "</ul>" + tab_content
    html_content += """
        <footer class="mt-5">
            <hr>
            <p class="text-center">Created by Matheus Gusmão and Júlia Marques</p>
        </footer>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

    # Ensure the output directory exists
    directory = os.path.dirname(output_html)
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Save the HTML file
    with open(output_html, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

    print(f"HTML file '{output_html}' created successfully!")


# %%
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO


def generate_html_analysis(df, output_html="output.html", max_categories=10):
    """
    Generates an HTML file with statistical analysis, charts for each column, and correlation analysis for numerical variables.

    Args:
        df (pd.DataFrame): The DataFrame to be analyzed.
        output_html (str): The name of the HTML file to be generated. Default is 'output.html'.
        max_categories (int): The maximum number of categories to display in bar charts. Default is 10.
    """

    # Configure matplotlib to use a font that supports Unicode characters
    plt.rcParams["font.family"] = "DejaVu Sans"

    # General settings for the plots
    sns.set_theme(style="whitegrid", palette="deep", context="notebook")

    # Start the HTML content with general information at the top
    shape_info = df.shape
    column_names = df.columns.tolist()
    num_duplicated_lines = df.duplicated().sum()
    num_missing_values = df.isna().sum().sum()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Analysis Report</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="container pt-4">
        <h1>Data Analysis Report</h1>
        <h2>General Information</h2>
        <p><strong>Shape:</strong> {shape_info[0]} rows, {shape_info[1]} columns</p>
        <p><strong>Column Names:</strong> {', '.join(column_names)}</p>
        <p><strong>Number of duplicated lines:</strong> {num_duplicated_lines}</p>
        <p><strong>Number of missing values (NaN/Null):</strong> {num_missing_values}</p>

        <ul class="nav nav-tabs" id="myTab" role="tablist">
    """

    tab_content = '<div class="tab-content" id="myTabContent">'

    # Generate statistics and charts for each column
    for i, column in enumerate(df.columns):
        active_class = "active" if i == 0 else ""
        show_class = "show" if i == 0 else ""
        aria_selected = "true" if i == 0 else "false"

        # Add a tab for each column
        html_content += f"""
        <li class="nav-item" role="presentation">
            <button class="nav-link {active_class}" id="{column}-tab" data-bs-toggle="tab" data-bs-target="#{column}" type="button" role="tab" aria-controls="{column}" aria-selected="{aria_selected}">{column}</button>
        </li>
        """

        # Add the content for the statistics and charts in the tab
        tab_content += f"""
        <div class="tab-pane fade {show_class}" id="{column}" role="tabpanel" aria-labelledby="{column}-tab">
            <h2>Analysis for column: {column}</h2>
        """

        # Get the statistics for the column
        stats = df[column].describe(include="all")

        # Add the statistics to the HTML, checking if the column is numeric or categorical
        if pd.api.types.is_numeric_dtype(df[column]):
            tab_content += f"""
            <p><strong>Count:</strong> {stats.get('count', 'N/A')}</p>
            <p><strong>Mean:</strong> {stats.get('mean', 'N/A')}</p>
            <p><strong>Standard Deviation:</strong> {stats.get('std', 'N/A')}</p>
            <p><strong>Min:</strong> {stats.get('min', 'N/A')}</p>
            <p><strong>25%:</strong> {stats.get('25%', 'N/A')}</p>
            <p><strong>Median:</strong> {stats.get('50%', 'N/A')}</p>
            <p><strong>75%:</strong> {stats.get('75%', 'N/A')}</p>
            <p><strong>Max:</strong> {stats.get('max', 'N/A')}</p>
            """

            # Generate the histogram for numeric columns
            plt.figure(figsize=(10, 6))
            sns.histplot(df[column].dropna(), bins=20, color="blue", kde=True)
            plt.title(f"Histogram of {column}")
            plt.xlabel(column)
            plt.ylabel("Frequency")
        else:
            # For categorical columns, show relevant statistics
            tab_content += f"""
            <p><strong>Count:</strong> {stats.get('count', 'N/A')}</p>
            <p><strong>Unique:</strong> {stats.get('unique', 'N/A')}</p>
            <p><strong>Top:</strong> {stats.get('top', 'N/A')}</p>
            <p><strong>Frequency of Top:</strong> {stats.get('freq', 'N/A')}</p>
            """

            # Filter the data for categorical columns to show only the top 'max_categories' categories
            value_counts = df[column].value_counts().head(max_categories)
            filtered_data = df[df[column].isin(value_counts.index)]

            # Generate the bar chart for categorical columns
            plt.figure(figsize=(10, 6))
            sns.countplot(
                x=column,
                data=filtered_data,
                order=value_counts.index,
                hue=column,
                dodge=False,
                palette="viridis",
                legend=False,
            )
            plt.title(f"Bar Chart of {column} (Top {max_categories} categories)")
            plt.xlabel(column)
            plt.ylabel("Frequency")
            plt.xticks(
                rotation=90
            )  # Rotate the x-axis labels by 90 degrees for better readability

        # Save the plot as a base64-encoded image
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight", facecolor="w")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plt.close()

        # Add the image to the tab content
        tab_content += (
            f'<img src="data:image/png;base64,{image_base64}" class="img-fluid" />'
        )
        tab_content += "</div>"

    # Add a tab for correlation analysis
    html_content += """
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="correlation-tab" data-bs-toggle="tab" data-bs-target="#correlation" type="button" role="tab" aria-controls="correlation" aria-selected="false">Correlation Analysis</button>
    </li>
    """
    tab_content += """
    <div class="tab-pane fade" id="correlation" role="tabpanel" aria-labelledby="correlation-tab">
        <h2>Correlation Analysis</h2>
    """

    # Generate the correlation heatmap for numeric columns
    numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns
    if len(numeric_columns) > 1:
        plt.figure(figsize=(12, 8))
        correlation_matrix = df[numeric_columns].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
        plt.title("Correlation Heatmap")

        # Save the heatmap as a base64-encoded image
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight", facecolor="w")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plt.close()

        # Add the heatmap to the tab content
        tab_content += (
            f'<img src="data:image/png;base64,{image_base64}" class="img-fluid" />'
        )

    tab_content += "</div>"  # Close the correlation tab content
    tab_content += "</div>"  # Close the tab content wrapper

    # Finish the HTML with the footer
    html_content += "</ul>" + tab_content
    html_content += """
        <footer class="mt-5">
            <hr>
            <p class="text-center">Created by Matheus Gusmão and Júlia Marques</p>
        </footer>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

    # Ensure the output directory exists
    directory = os.path.dirname(output_html)
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Save the HTML file
    with open(output_html, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

    print(f"HTML file '{output_html}' created successfully!")


# %%
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO


def generate_html_analysis(df, output_html="output.html", max_categories=10):
    """
    Generates an HTML file with statistical analysis, charts for each column, and correlation analysis for numerical variables.

    Args:
        df (pd.DataFrame): The DataFrame to be analyzed.
        output_html (str): The name of the HTML file to be generated. Default is 'output.html'.
        max_categories (int): The maximum number of categories to display in bar charts. Default is 10.
    """

    # Configure matplotlib to use a font that supports CJK characters
    plt.rcParams["font.family"] = "Noto Sans CJK JP"

    # General settings for the plots
    sns.set_theme(style="whitegrid", palette="deep", context="notebook")

    # Start the HTML content with general information at the top
    shape_info = df.shape
    column_names = df.columns.tolist()
    num_duplicated_lines = df.duplicated().sum()
    num_missing_values = df.isna().sum().sum()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Analysis Report</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="container pt-4">
        <h1>Data Analysis Report</h1>
        <h2>General Information</h2>
        <p><strong>Shape:</strong> {shape_info[0]} rows, {shape_info[1]} columns</p>
        <p><strong>Column Names:</strong> {', '.join(column_names)}</p>
        <p><strong>Number of duplicated lines:</strong> {num_duplicated_lines}</p>
        <p><strong>Number of missing values (NaN/Null):</strong> {num_missing_values}</p>

        <ul class="nav nav-tabs" id="myTab" role="tablist">
    """

    tab_content = '<div class="tab-content" id="myTabContent">'

    # Generate statistics and charts for each column
    for i, column in enumerate(df.columns):
        active_class = "active" if i == 0 else ""
        show_class = "show" if i == 0 else ""
        aria_selected = "true" if i == 0 else "false"

        # Add a tab for each column
        html_content += f"""
        <li class="nav-item" role="presentation">
            <button class="nav-link {active_class}" id="{column}-tab" data-bs-toggle="tab" data-bs-target="#{column}" type="button" role="tab" aria-controls="{column}" aria-selected="{aria_selected}">{column}</button>
        </li>
        """

        # Add the content for the statistics and charts in the tab
        tab_content += f"""
        <div class="tab-pane fade {show_class}" id="{column}" role="tabpanel" aria-labelledby="{column}-tab">
            <h2>Analysis for column: {column}</h2>
        """

        # Get the statistics for the column
        stats = df[column].describe(include="all")

        # Add the statistics to the HTML, checking if the column is numeric or categorical
        if pd.api.types.is_numeric_dtype(df[column]):
            tab_content += f"""
            <p><strong>Count:</strong> {stats.get('count', 'N/A')}</p>
            <p><strong>Mean:</strong> {stats.get('mean', 'N/A')}</p>
            <p><strong>Standard Deviation:</strong> {stats.get('std', 'N/A')}</p>
            <p><strong>Min:</strong> {stats.get('min', 'N/A')}</p>
            <p><strong>25%:</strong> {stats.get('25%', 'N/A')}</p>
            <p><strong>Median:</strong> {stats.get('50%', 'N/A')}</p>
            <p><strong>75%:</strong> {stats.get('75%', 'N/A')}</p>
            <p><strong>Max:</strong> {stats.get('max', 'N/A')}</p>
            """

            # Generate the histogram for numeric columns
            plt.figure(figsize=(10, 6))
            sns.histplot(df[column].dropna(), bins=20, color="blue", kde=True)
            plt.title(f"Histogram of {column}")
            plt.xlabel(column)
            plt.ylabel("Frequency")
        else:
            # For categorical columns, show relevant statistics
            tab_content += f"""
            <p><strong>Count:</strong> {stats.get('count', 'N/A')}</p>
            <p><strong>Unique:</strong> {stats.get('unique', 'N/A')}</p>
            <p><strong>Top:</strong> {stats.get('top', 'N/A')}</p>
            <p><strong>Frequency of Top:</strong> {stats.get('freq', 'N/A')}</p>
            """

            # Filter the data for categorical columns to show only the top 'max_categories' categories
            value_counts = df[column].value_counts().head(max_categories)
            filtered_data = df[df[column].isin(value_counts.index)]

            # Generate the bar chart for categorical columns
            plt.figure(figsize=(10, 6))
            sns.countplot(
                x=column,
                data=filtered_data,
                order=value_counts.index,
                hue=column,
                dodge=False,
                palette="viridis",
                legend=False,
            )
            plt.title(f"Bar Chart of {column} (Top {max_categories} categories)")
            plt.xlabel(column)
            plt.ylabel("Frequency")
            plt.xticks(
                rotation=90
            )  # Rotate the x-axis labels by 90 degrees for better readability

        # Save the plot as a base64-encoded image
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight", facecolor="w")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plt.close()

        # Add the image to the tab content
        tab_content += (
            f'<img src="data:image/png;base64,{image_base64}" class="img-fluid" />'
        )
        tab_content += "</div>"

    # Add a tab for correlation analysis
    html_content += """
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="correlation-tab" data-bs-toggle="tab" data-bs-target="#correlation" type="button" role="tab" aria-controls="correlation" aria-selected="false">Correlation Analysis</button>
    </li>
    """
    tab_content += """
    <div class="tab-pane fade" id="correlation" role="tabpanel" aria-labelledby="correlation-tab">
        <h2>Correlation Analysis</h2>
    """

    # Generate the correlation heatmap for numeric columns
    numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns
    if len(numeric_columns) > 1:
        plt.figure(figsize=(12, 8))
        correlation_matrix = df[numeric_columns].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
        plt.title("Correlation Heatmap")

        # Save the heatmap as a base64-encoded image
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight", facecolor="w")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plt.close()

        # Add the heatmap to the tab content
        tab_content += (
            f'<img src="data:image/png;base64,{image_base64}" class="img-fluid" />'
        )

    tab_content += "</div>"  # Close the correlation tab content
    tab_content += "</div>"  # Close the tab content wrapper

    # Finish the HTML with the footer
    html_content += "</ul>" + tab_content
    html_content += """
        <footer class="mt-5">
            <hr>
            <p class="text-center">Created by Matheus Gusmão and Júlia Marques</p>
        </footer>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

    # Ensure the output directory exists
    directory = os.path.dirname(output_html)
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Save the HTML file
    with open(output_html, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

    print(f"HTML file '{output_html}' created successfully!")
