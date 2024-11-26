import pandas as pd
import graphviz
from typing import List, Dict, Any
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
        """
        Generate a flowchart for the specified empowered entity and triggering event.
        """
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
        
        # Create main entity and trigger nodes with rank constraints
        with dot.subgraph(name='cluster_top') as top:
            top.attr(rank='min')  # Force to top
            top.node('entity', self.wrap_text(entity), 
                    shape='box', style='filled', fillcolor='lightblue')
        
        with dot.subgraph(name='cluster_trigger') as trigger_level:
            trigger_level.attr(rank='same')  # Force to same level
            trigger_level.node('trigger', self.wrap_text(trigger), 
                    shape='diamond', style='filled', fillcolor='lightgreen')
        
        dot.edge('entity', 'trigger')
        
        # Process each row as a complete unit
        for idx, row in filtered_df.iterrows():
            cluster_name = f'cluster_group_{idx}'
            with dot.subgraph(name=cluster_name) as group:
                group.attr(label=f'Power Group {idx + 1}', style='filled', fillcolor='white')
                
                # Create citation node
                citation = f"{row['Citation']} {row['Parent.Statute']}"
                if not pd.isna(citation):
                    citation_id = f'citation_{idx}'
                    group.node(citation_id, self.wrap_text(f"Citation:\n{citation}"),
                            shape='box', style='filled', fillcolor='lightyellow')
                    dot.edge('trigger', citation_id)
                    
                    # Add implementation details directly connected to citation
                    if not pd.isna(row['Document.Description']):
                        desc_id = f'desc_{idx}'
                        group.node(desc_id, self.wrap_text(f"Implementation:\n{row['Document.Description']}"),
                                shape='box', style='filled', fillcolor='lightgray')
                        dot.edge(citation_id, desc_id)
                    
                    # Add health emergency details connected to citation
                    if not pd.isna(row['Describe.Health.Emergency']):
                        health_id = f'health_{idx}'
                        group.node(health_id, self.wrap_text(f"Health Impact:\n{row['Describe.Health.Emergency']}"),
                                shape='box', style='filled', fillcolor='mistyrose')
                        dot.edge(citation_id, health_id)
                    
                    # Add military involvement if present
                    if not pd.isna(row['Military.Involvement..Federal.']):
                        military_id = f'military_{idx}'
                        group.node(military_id, self.wrap_text(f"Military Involvement:\n{row['Military.Involvement..Federal.']}"),
                                shape='box', style='filled', fillcolor='lightpink')
                        dot.edge(citation_id, military_id)
                    
                    # Add funding information if present
                    if not pd.isna(row['Funding.Stream.']):
                        funding_id = f'funding_{idx}'
                        funding_text = row['Funding.Stream.']
                        if not pd.isna(row['Funding.Stream.Description']):
                            funding_text += f"\n{row['Funding.Stream.Description']}"
                        group.node(funding_id, self.wrap_text(f"Funding:\n{funding_text}"),
                                shape='box', style='filled', fillcolor='lightgreen')
                        dot.edge(citation_id, funding_id)

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
    
    print("\nAvailable Empowered Entities:")
    for entity in generator.get_available_entities():
        print(f"- {entity}")
    
    print("\nAvailable Triggering Events:")
    for trigger in generator.get_available_triggers():
        print(f"- {trigger}")
    
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

