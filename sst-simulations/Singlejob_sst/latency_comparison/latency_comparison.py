import matplotlib.pyplot as plt
import pandas as pd
import os

# --- Manually collected data ---
# Ensure these lists have the exact same number of elements.
simulation_data = {
    'Simulation Type': [
        'Mesh Allreduce (4 ranks)',
        'PolarFly Allreduce (13 ranks)',
        'Dragonfly Allreduce (32 ranks)'
    ],
    'Latency (us)': [
        2.074,  # For Mesh
        3.939,  # For PolarFly
        5.269   # For Dragonfly
    ]
}

def plot_latency_comparison(data):
    """
    Plots a bar chart comparing latencies of different simulations.
    """
    # --- Debugging: Print list lengths ---
    print(f"Debug: Length of 'Simulation Type' list: {len(data['Simulation Type'])}")
    print(f"Debug: Length of 'Latency (us)' list: {len(data['Latency (us)'])}")
    # --- End Debugging ---

    df = pd.DataFrame(data)

    plt.figure(figsize=(8, 7))
    bars = plt.bar(df['Simulation Type'], df['Latency (us)'], color=['lightcoral', 'lightgreen', 'lightblue'])
    plt.xlabel("Simulation Type")
    plt.ylabel("Latency (microseconds)")
    plt.title("Latency Comparison Across Topologies")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 3), ha='center', va='bottom')

    plt.savefig("simulation_latency_comparison.png")
    plt.show()
    print(f"Plot saved as simulation_latency_comparison.png in {os.getcwd()}")


if __name__ == "__main__":
    plot_latency_comparison(simulation_data)
