import pandas as pd
import graphviz
from typing import List, Dict, Any
import inquirer
import textwrap

class EmergencyPowerFlowchartGenerator:
    def __init__(self, data_path: str):
        """
        Initialize the flowchart generator with the emergency powers dataset.
        """
        self.df = pd.read_csv(data_path)
        self.entities = sorted(self.df['Entity.Empowered'].unique())
        self.triggers = sorted(self.df['Triggering.Event'].dropna().unique())
        
    def wrap_text(self, text: str, width: int = 40) -> str:
        """Wrap text to specified width for better visualization."""
        if pd.isna(text):
            return "N/A"
        return '\n'.join(textwrap.wrap(str(text), width=width))
    
    def get_available_entities(self) -> List[str]:
        """Return list of available empowered entities."""
        return self.entities
    
    def get_available_triggers(self) -> List[str]:
        """Return list of available triggering events."""
        return self.triggers
    
    def generate_flowchart(self, entity: str, trigger: str) -> graphviz.Digraph:
        # Filter data for the specific entity and trigger
        filtered_df = self.df[
            (self.df['Entity.Empowered'] == entity) & 
            (self.df['Triggering.Event'].str.contains(trigger, na=False))
        ]
        
        if filtered_df.empty:
            raise ValueError(f"No data found for entity '{entity}' and trigger '{trigger}'")
        
        # Create a new directed graph with adjusted settings
        dot = graphviz.Digraph(comment=f'{entity} - {trigger} Power Flow')
        dot.attr(rankdir='TB', size='40,40', dpi='600')
        
        # Create main entity node at top
        with dot.subgraph(name='cluster_top') as top:
            top.attr(rank='min')
            top.node('entity', self.wrap_text(entity), 
                    shape='box', style='filled', fillcolor='lightblue')
        
        # Create triggering event node
        with dot.subgraph(name='cluster_trigger') as trigger_level:
            trigger_level.attr(rank='same')
            trigger_level.node('trigger', self.wrap_text(trigger), 
                    shape='diamond', style='filled', fillcolor='lightgreen')
        
        dot.edge('entity', 'trigger')
        
        # Group by unique locations
        locations = filtered_df['Location'].unique()
        
        # Create a node for each unique location
        for loc in locations:
            loc_id = f'location_{loc.lower().replace(" ", "_")}'
            dot.node(loc_id, self.wrap_text(f"Location:\n{loc}"),
                    shape='box', style='filled', fillcolor='lightyellow')
            dot.edge('trigger', loc_id)
            
            # Filter rows for this location
            loc_rows = filtered_df[filtered_df['Location'] == loc]
            
            # Add all powers for this location
            for idx, row in loc_rows.iterrows():
                if not pd.isna(row['Document.Description']):
                    power_id = f'power_{idx}'
                    dot.node(power_id, self.wrap_text(f"Power:\n{row['Document.Description']}"),
                            shape='box', style='filled', fillcolor='lightgray')
                    dot.edge(loc_id, power_id)
                    
                    # Add citation connected to power
                    citation = f"{row['Citation']} {row['Parent.Statute']}"
                    if not pd.isna(citation):
                        citation_id = f'citation_{idx}'
                        dot.node(citation_id, self.wrap_text(f"Citation:\n{citation}"),
                                shape='box', style='filled', fillcolor='mistyrose')
                        dot.edge(power_id, citation_id)
        
        return dot
        
    def save_flowchart(self, dot: graphviz.Digraph, output_path: str, format: str = 'png') -> None:
        dot.attr(bgcolor='white')    # Ensure white background
        dot.attr(size='40,40')       # Much larger size
        dot.attr(dpi='600')          # Double the DPI
        # Add font size settings for better readability
        dot.attr('node', fontsize='24')  # Increase node text size
        dot.attr('edge', fontsize='20')  # Increase edge text size
        dot.attr('graph', fontsize='28') # Increase graph label size
        dot.render(output_path, format=format, cleanup=True)

def main():
    csv_path = 'CleanDataLong.csv'  # Update with your CSV file name
    
    print("\nInitializing generator and reading CSV file...")
    generator = EmergencyPowerFlowchartGenerator(csv_path)
    
    
    # Get input from user
    entity = input("\nEnter empowered entity: ")
    trigger = input("Enter triggering event: ")
    
    # Generate and save flowchart
    try:
        flowchart = generator.generate_flowchart(entity, trigger)
        output_path = f"flowchart_{entity.lower().replace(' ', '_')}_{trigger.lower().replace(' ', '_')}"
        generator.save_flowchart(flowchart, output_path)
        print(f"\nFlowchart has been generated and saved as '{output_path}.png'")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

