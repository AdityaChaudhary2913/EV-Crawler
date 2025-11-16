"""
Knowledge Graph Builder for EV domain.
Constructs a property graph from entities and relations using NetworkX.
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
import networkx as nx

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ner.entity_extractor import Entity
from relation_extraction.relation_extractor import Relation


class KnowledgeGraph:
    """
    Property graph representation of knowledge.
    Uses NetworkX for graph operations.
    """
    
    def __init__(self):
        """Initialize empty knowledge graph."""
        self.graph = nx.MultiDiGraph()  # Allows multiple edges between nodes
        self.entity_to_node = {}  # Map normalized entity text to node ID
        self.node_counter = 0
    
    def add_entity(self, entity: Entity) -> str:
        """
        Add an entity as a node in the graph.
        
        Args:
            entity: Entity object
        
        Returns:
            Node ID
        """
        # Use normalized text as key
        key = entity.normalized_text
        
        # If entity already exists, update properties
        if key in self.entity_to_node:
            node_id = self.entity_to_node[key]
            # Update confidence if higher
            if self.graph.nodes[node_id]['confidence'] < entity.confidence:
                self.graph.nodes[node_id]['confidence'] = entity.confidence
                self.graph.nodes[node_id]['text'] = entity.text
            # Increment frequency
            self.graph.nodes[node_id]['frequency'] += 1
            return node_id
        
        # Create new node
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        
        self.graph.add_node(
            node_id,
            text=entity.text,
            normalized_text=entity.normalized_text,
            entity_type=entity.entity_type,
            confidence=entity.confidence,
            source=entity.source,
            frequency=1
        )
        
        self.entity_to_node[key] = node_id
        
        return node_id
    
    def add_relation(self, relation: Relation) -> bool:
        """
        Add a relation as an edge in the graph.
        
        Args:
            relation: Relation object
        
        Returns:
            True if added, False if skipped
        """
        # Add entities first (if not already in graph)
        source_id = self.add_entity(relation.entity1)
        target_id = self.add_entity(relation.entity2)
        
        # Don't add self-loops
        if source_id == target_id:
            return False
        
        # Add edge with properties
        self.graph.add_edge(
            source_id,
            target_id,
            relation_type=relation.relation_type,
            confidence=relation.confidence,
            context=relation.context[:200]  # Truncate context
        )
        
        return True
    
    def build_from_relations(self, relations: List[Relation]) -> None:
        """
        Build graph from list of relations.
        
        Args:
            relations: List of Relation objects
        """
        for relation in relations:
            self.add_relation(relation)
    
    def get_node_by_text(self, text: str) -> str:
        """
        Get node ID by entity text (normalized).
        
        Args:
            text: Entity text (will be normalized)
        
        Returns:
            Node ID or None if not found
        """
        normalized = text.lower().strip()
        return self.entity_to_node.get(normalized)
    
    def get_neighbors(self, node_id: str, relation_type: str = None) -> List[Tuple[str, Dict]]:
        """
        Get neighbors of a node.
        
        Args:
            node_id: Node ID
            relation_type: Optional filter by relation type
        
        Returns:
            List of (neighbor_id, edge_data) tuples
        """
        if node_id not in self.graph:
            return []
        
        neighbors = []
        for neighbor_id in self.graph.successors(node_id):
            # Get all edges between node_id and neighbor_id
            edges = self.graph.get_edge_data(node_id, neighbor_id)
            for edge_key, edge_data in edges.items():
                if relation_type is None or edge_data['relation_type'] == relation_type:
                    neighbors.append((neighbor_id, edge_data))
        
        return neighbors
    
    def get_node_properties(self, node_id: str) -> Dict:
        """Get all properties of a node."""
        if node_id not in self.graph:
            return {}
        return dict(self.graph.nodes[node_id])
    
    def get_statistics(self) -> Dict:
        """
        Calculate graph statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'nodes_by_type': defaultdict(int),
            'edges_by_relation': defaultdict(int),
            'avg_degree': 0.0,
            'density': 0.0,
            'num_connected_components': 0,
            'largest_component_size': 0
        }
        
        # Count nodes by type
        for node_id in self.graph.nodes():
            entity_type = self.graph.nodes[node_id]['entity_type']
            stats['nodes_by_type'][entity_type] += 1
        
        # Count edges by relation type
        for u, v, data in self.graph.edges(data=True):
            relation_type = data['relation_type']
            stats['edges_by_relation'][relation_type] += 1
        
        # Calculate metrics
        if stats['num_nodes'] > 0:
            stats['avg_degree'] = stats['num_edges'] / stats['num_nodes']
            stats['density'] = nx.density(self.graph)
        
        # Connected components (treating as undirected for this purpose)
        undirected = self.graph.to_undirected()
        components = list(nx.connected_components(undirected))
        stats['num_connected_components'] = len(components)
        if components:
            stats['largest_component_size'] = len(max(components, key=len))
        
        # Convert defaultdicts to regular dicts
        stats['nodes_by_type'] = dict(stats['nodes_by_type'])
        stats['edges_by_relation'] = dict(stats['edges_by_relation'])
        
        return stats
    
    def get_top_entities(self, n: int = 10, entity_type: str = None) -> List[Tuple[str, Dict]]:
        """
        Get top N entities by degree (most connected).
        
        Args:
            n: Number of entities to return
            entity_type: Optional filter by entity type
        
        Returns:
            List of (node_id, properties) tuples
        """
        # Filter nodes by type if specified
        if entity_type:
            nodes = [
                node_id for node_id in self.graph.nodes()
                if self.graph.nodes[node_id]['entity_type'] == entity_type
            ]
        else:
            nodes = list(self.graph.nodes())
        
        # Calculate degree for each node
        node_degrees = [(node_id, self.graph.degree(node_id)) for node_id in nodes]
        
        # Sort by degree (descending)
        node_degrees.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N with properties
        return [
            (node_id, self.get_node_properties(node_id))
            for node_id, _ in node_degrees[:n]
        ]
    
    def export_to_dict(self) -> Dict:
        """
        Export graph to dictionary format.
        
        Returns:
            Dictionary with nodes and edges
        """
        nodes = []
        for node_id in self.graph.nodes():
            node_data = dict(self.graph.nodes[node_id])
            node_data['id'] = node_id
            nodes.append(node_data)
        
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edge_data = dict(data)
            edge_data['source'] = u
            edge_data['target'] = v
            edges.append(edge_data)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'statistics': self.get_statistics()
        }
    
    def save_to_json(self, filepath: Path) -> None:
        """
        Save graph to JSON file.
        
        Args:
            filepath: Path to output file
        """
        data = self.export_to_dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_json(self, filepath: Path) -> None:
        """
        Load graph from JSON file.
        
        Args:
            filepath: Path to input file
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Clear existing graph
        self.graph.clear()
        self.entity_to_node.clear()
        self.node_counter = 0
        
        # Add nodes
        for node_data in data['nodes']:
            node_id = node_data.pop('id')
            self.graph.add_node(node_id, **node_data)
            self.entity_to_node[node_data['normalized_text']] = node_id
            # Update counter
            node_num = int(node_id.split('_')[1])
            if node_num >= self.node_counter:
                self.node_counter = node_num + 1
        
        # Add edges
        for edge_data in data['edges']:
            source = edge_data.pop('source')
            target = edge_data.pop('target')
            self.graph.add_edge(source, target, **edge_data)
    
    def get_subgraph(self, node_ids: List[str]) -> 'KnowledgeGraph':
        """
        Extract a subgraph containing specified nodes.
        
        Args:
            node_ids: List of node IDs to include
        
        Returns:
            New KnowledgeGraph object with subgraph
        """
        subgraph_nx = self.graph.subgraph(node_ids).copy()
        
        kg = KnowledgeGraph()
        kg.graph = subgraph_nx
        
        # Rebuild entity_to_node mapping
        for node_id in kg.graph.nodes():
            normalized_text = kg.graph.nodes[node_id]['normalized_text']
            kg.entity_to_node[normalized_text] = node_id
        
        return kg
    
    def find_paths(self, source_text: str, target_text: str, max_length: int = 3) -> List[List[str]]:
        """
        Find paths between two entities.
        
        Args:
            source_text: Source entity text
            target_text: Target entity text
            max_length: Maximum path length
        
        Returns:
            List of paths (each path is a list of node IDs)
        """
        source_id = self.get_node_by_text(source_text)
        target_id = self.get_node_by_text(target_text)
        
        if not source_id or not target_id:
            return []
        
        try:
            paths = list(nx.all_simple_paths(
                self.graph,
                source_id,
                target_id,
                cutoff=max_length
            ))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def query_relations(
        self,
        entity_text: str = None,
        entity_type: str = None,
        relation_type: str = None
    ) -> List[Dict]:
        """
        Query for relations matching criteria.
        
        Args:
            entity_text: Filter by entity text (source or target)
            entity_type: Filter by entity type (source or target)
            relation_type: Filter by relation type
        
        Returns:
            List of relation dictionaries
        """
        results = []
        
        for u, v, data in self.graph.edges(data=True):
            # Check relation type
            if relation_type and data['relation_type'] != relation_type:
                continue
            
            source_props = self.graph.nodes[u]
            target_props = self.graph.nodes[v]
            
            # Check entity text
            if entity_text:
                normalized = entity_text.lower().strip()
                if (source_props['normalized_text'] != normalized and
                    target_props['normalized_text'] != normalized):
                    continue
            
            # Check entity type
            if entity_type:
                if (source_props['entity_type'] != entity_type and
                    target_props['entity_type'] != entity_type):
                    continue
            
            # Add to results
            results.append({
                'source': source_props['text'],
                'source_type': source_props['entity_type'],
                'relation': data['relation_type'],
                'target': target_props['text'],
                'target_type': target_props['entity_type'],
                'confidence': data['confidence']
            })
        
        return results


def visualize_graph_statistics(kg: KnowledgeGraph) -> str:
    """
    Create a text visualization of graph statistics.
    
    Args:
        kg: KnowledgeGraph object
    
    Returns:
        Formatted string with statistics
    """
    stats = kg.get_statistics()
    
    output = []
    output.append("=" * 60)
    output.append("KNOWLEDGE GRAPH STATISTICS")
    output.append("=" * 60)
    output.append("")
    output.append(f"Nodes: {stats['num_nodes']}")
    output.append(f"Edges: {stats['num_edges']}")
    output.append(f"Average degree: {stats['avg_degree']:.2f}")
    output.append(f"Density: {stats['density']:.4f}")
    output.append(f"Connected components: {stats['num_connected_components']}")
    output.append(f"Largest component: {stats['largest_component_size']} nodes")
    output.append("")
    
    output.append("Nodes by type:")
    for entity_type, count in sorted(stats['nodes_by_type'].items(), key=lambda x: x[1], reverse=True):
        output.append(f"  {entity_type}: {count}")
    output.append("")
    
    output.append("Edges by relation:")
    for relation_type, count in sorted(stats['edges_by_relation'].items(), key=lambda x: x[1], reverse=True):
        output.append(f"  {relation_type}: {count}")
    output.append("")
    
    return '\n'.join(output)
