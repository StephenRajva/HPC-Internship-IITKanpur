import pandas as pd
import matplotlib.pyplot as plt
import os

POLARFLY_CSV_PATH = "polarfly_stats.csv"

def plot_polarfly_hop_counts(csv_path):
    """
    Reads the PolarFly statistics CSV and plots the aggregated hop counts.
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}", flush=True)
        return

    try:
        df_stats = pd.read_csv(csv_path)

        # Strip whitespace from column names
        df_stats.columns = df_stats.columns.str.strip()

        # Filter for polarfly components and hopcount statistics
        polarfly_hops = df_stats[
            (df_stats['ComponentName'].str.startswith('polarfly_network.r')) &
            (df_stats['ComponentName'].str.endswith(':topology')) &
            (df_stats['StatisticName'].str.strip().str.startswith('hopcount'))
        ]

        aggregated_hops = polarfly_hops.groupby('StatisticName')['Sum.u32'].sum()

        if aggregated_hops.empty or aggregated_hops.sum() == 0:
            print("No hop count statistics found or all aggregated hop counts are zero. Please check 'ComponentName' and 'StatisticName' filters, and the 'Sum.u32' column.", flush=True)
            print("\nAvailable ComponentNames (after stripping):", df_stats['ComponentName'].unique(), flush=True)
            print("Available StatisticNames (after stripping):", df_stats['StatisticName'].unique(), flush=True)
            print("Aggregated Hops (if any):", aggregated_hops, flush=True)
            return

        # Prepare data for plotting
        hop_labels = [s.strip().replace('hopcount', '') for s in aggregated_hops.index]
        hop_counts = aggregated_hops.values

        # Create a DataFrame for plotting and sort by hop number
        plot_df = pd.DataFrame({'Hops': hop_labels, 'Packet Count': hop_counts})
        plot_df['Hops_Int'] = plot_df['Hops'].astype(int)
        plot_df = plot_df.sort_values(by='Hops_Int')

        # Create the bar chart
        plt.figure(figsize=(8, 6))
        bars = plt.bar(plot_df['Hops'], plot_df['Packet Count'], color='skyblue')
        plt.xlabel("Number of Hops")
        plt.ylabel("Total Packet Count")
        plt.title("PolarFly (q=3) Allreduce: Aggregated Packet Hop Counts")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(plot_df['Hops'])
        plt.tight_layout()

        for bar in bars:
            yval = bar.get_height()
            # FIX: Convert the integer yval to string before passing to plt.text
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, str(int(yval)), ha='center', va='bottom')

        plt.savefig("polarfly_hop_counts_bar_chart.png")
        plt.show()
        print(f"Plot saved as polarfly_hop_counts_bar_chart.png in {os.getcwd()}", flush=True)

    except pd.errors.EmptyDataError:
        print(f"Error: CSV file at {csv_path} is empty or malformed.", flush=True)
    except KeyError as ke:
        print(f"Error: Missing expected column in CSV: {ke}. Please check column names in the CSV.", flush=True)
        print("Available columns:", df_stats.columns.tolist(), flush=True)
    except Exception as e:
        print(f"An unexpected error occurred while plotting: {e}", flush=True)
        print("Please ensure the CSV file is correctly formatted and pandas/matplotlib are installed.", flush=True)

if __name__ == "__main__":
    plot_polarfly_hop_counts(POLARFLY_CSV_PATH)
