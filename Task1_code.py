import pandas as pd
import networkx as nx

node_mapping = {
    'B': 'Berlin', 'D': 'Düsseldorf', 'DO': 'Dortmund', 'F': 'Frankfurt',
    'H': 'Hannover', 'HH': 'Hamburg', 'K': 'Köln', 'L': 'Leipzig',
    'M': 'München', 'N': 'Nürnberg', 'S': 'Stuttgart', 'ULM': 'Ulm'
}

traffic_matrix = pd.read_csv('./Traffic_matrix.csv', index_col=0, encoding='latin1')
traffic_matrix = traffic_matrix.rename(index=node_mapping, columns=node_mapping)

topology = pd.read_excel('./topology.xlsx')

G = nx.Graph()
for _, row in topology.iterrows():
    G.add_edge(row['Node-A'], row['Node-Z'], weight=row['Length'])

shortest_paths = {}
for source in traffic_matrix.columns:
    for target in traffic_matrix.index:
        if source != target:
            shortest_paths[(source, target)] = nx.shortest_path(G, source=source, target=target, weight='weight')

link_traffic = {edge: 0 for edge in G.edges}
for (src, dst), path in shortest_paths.items():
    flow_size = traffic_matrix.loc[src, dst]
    for i in range(len(path) - 1):
        link = (path[i], path[i + 1])
        if link not in link_traffic:
            link = (link[1], link[0])
        link_traffic[link] += flow_size

def calculate_capacity(traffic):
    num_40 = traffic // 40
    num_100 = traffic // 100
    remainder_40 = traffic % 40
    remainder_100 = traffic % 100
    
    if remainder_40 == 0:
        return num_40 * 40
    if remainder_100 == 0:
        return num_100 * 100
    
    cap_40 = (num_40 + 1) * 40
    cap_100 = (num_100 + 1) * 100
    
    if cap_40 - traffic < cap_100 - traffic:
        return cap_40
    return cap_100

link_capacities = {link: calculate_capacity(traffic) for link, traffic in link_traffic.items()}

total_network_capacity = sum(link_capacities.values())

with pd.ExcelWriter('./Task1_output.xlsx') as writer:
    shortest_paths_df = pd.DataFrame(list(shortest_paths.items()), columns=['Traffic Flow', 'Shortest Path'])
    shortest_paths_df.to_excel(writer, sheet_name='Shortest Paths', index=False)
    link_traffic_df = pd.DataFrame(list(link_traffic.items()), columns=['Link', 'Total Traffic (Gb/s)'])
    link_traffic_df.to_excel(writer, sheet_name='Link Traffic', index=False)
    link_capacity_df = pd.DataFrame(list(link_capacities.items()), columns=['Link', 'Capacity (Gb/s)'])
    link_capacity_df.to_excel(writer, sheet_name='Link Capacity', index=False)
    total_network_capacity_df = pd.DataFrame([['Total Network Capacity', total_network_capacity]], columns=['Metric', 'Value'])
    total_network_capacity_df.to_excel(writer, sheet_name='Total Network Capacity', index=False)
