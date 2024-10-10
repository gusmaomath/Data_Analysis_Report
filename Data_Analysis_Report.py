# %%
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO


# %%
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
        <nav class="d-flex align-items-center gap-3 mb-4">
            <svg style="height: 50px;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                <path d="M448 80l0 48c0 44.2-100.3 80-224 80S0 172.2 0 128L0 80C0 35.8 100.3 0 224 0S448 35.8 448 80zM393.2 214.7c20.8-7.4 39.9-16.9 54.8-28.6L448 288c0 44.2-100.3 80-224 80S0 332.2 0 288L0 186.1c14.9 11.8 34 21.2 54.8 28.6C99.7 230.7 159.5 240 224 240s124.3-9.3 169.2-25.3zM0 346.1c14.9 11.8 34 21.2 54.8 28.6C99.7 390.7 159.5 400 224 400s124.3-9.3 169.2-25.3c20.8-7.4 39.9-16.9 54.8-28.6l0 85.9c0 44.2-100.3 80-224 80S0 476.2 0 432l0-85.9z"/>
            </svg>
            <h1>Data Analysis Report</h1>
        </nav>

        <h3>Dataset's General Information</h3>
        <p>
            <strong>Shape:</strong> {shape_info[0]} rows, {shape_info[1]} columns <br>
            <strong>Number of duplicated lines:</strong> {num_duplicated_lines} <br>
            <strong>Number of missing values (NaN/Null):</strong> {num_missing_values}
        </p>

        <div class="row">
            <div class="col-4">
                <div class="list-group" id="list-tab" role="tablist">
    """

    tab_content = """
            <div class="col-8">
                <div class="tab-content" id="nav-tabContent">
    """

    # Generate statistics and charts for each column
    for i, column in enumerate(df.columns):
        active_class = "active" if i == 0 else ""
        show_class = "show" if i == 0 else ""

        # Add a tab for each column
        html_content += f"""
                <a class="list-group-item list-group-item-action {active_class}" id="{column}-tab" data-bs-toggle="list" href="#{column}" role="tab" aria-controls="{column}">{column}</a>
        """

        # Add the content for the statistics and charts in the tab
        tab_content += f"""
        <div class="tab-pane fade {show_class} {active_class}" id="{column}" role="tabpanel" aria-labelledby="{column}-tab">
            <h2>Analysis for column: {column}</h2>
        """

        # Get the statistics for the column
        stats = df[column].describe(include="all")
        num_missing = df[column].isna().sum()

        # Add the statistics to the HTML, checking if the column is numeric or categorical
        if pd.api.types.is_numeric_dtype(df[column]):
            tab_content += f"""
            <p><strong>Count:</strong> {stats.get('count', 'N/A')}</p>
            <strong>Mean:</strong> {stats.get('mean', 'N/A')} <br>
            <strong>Standard Deviation:</strong> {stats.get('std', 'N/A')}<br>
            <strong>Min:</strong> {stats.get('min', 'N/A')}<br>
            <strong>25%:</strong> {stats.get('25%', 'N/A')}<br>
            <strong>Median:</strong> {stats.get('50%', 'N/A')}<br>
            <strong>75%:</strong> {stats.get('75%', 'N/A')}<br>
            <strong>Max:</strong> {stats.get('max', 'N/A')}<br>
            <strong>Missing Values (NaN/Null):</strong> {num_missing}</p>
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
            <p><strong>Missing Values (NaN/Null):</strong> {num_missing}</p>
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
            plt.xticks(rotation=90)

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
                <a class="list-group-item list-group-item-action" id="correlation-tab" data-bs-toggle="list" href="#correlation" role="tab" aria-controls="correlation">Correlation Analysis</a>
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
    html_content += (
        """
            </div> 
            </div> 
    """
        + tab_content
    )
    html_content += """
        </div> 
        </div> 
        <footer class="mt-5">
            <hr>
            <p class="text-center">Created by Matheus Gusmão, Júlia Marques, and Guilherme Morais</p>
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
