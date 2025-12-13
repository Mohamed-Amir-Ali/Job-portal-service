# storage_virtual_node.py
"""
Storage Virtual Node Module
Implements a virtual storage node with CPU, memory, and storage resources.
"""

class StorageVirtualNode:
    """Represents a virtual node in a storage network."""
    
    def __init__(self, node_id, cpu_capacity, memory_capacity, storage_capacity, bandwidth):
        """
        Initialize a storage virtual node.
        
        Args:
            node_id (str): Unique identifier for the node
            cpu_capacity (int): CPU cores available
            memory_capacity (int): Memory in GB
            storage_capacity (int): Storage capacity in MB
            bandwidth (int): Network bandwidth in Mbps
        """
        self.id = node_id
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.storage_capacity = storage_capacity
        self.bandwidth = bandwidth
        self.used_storage = 0
        self.active_transfers = set()
    
    def allocate_storage(self, size):
        """Allocate storage space for a file."""
        if self.used_storage + size <= self.storage_capacity:
            self.used_storage += size
            return True
        return False
    
    def free_storage(self, size):
        """Free up storage space."""
        self.used_storage = max(0, self.used_storage - size)
    
    def get_storage_utilization(self):
        """Get current storage utilization statistics."""
        return {
            'used': self.used_storage,
            'capacity': self.storage_capacity,
            'utilization_percent': (self.used_storage / self.storage_capacity) * 100
        }


# storage_virtual_network.py
"""
Storage Virtual Network Module
Implements a virtual network for simulating file transfers between nodes.
"""

import math

class FileTransfer:
    """Represents a file transfer between two nodes."""
    
    def __init__(self, file_id, source, target, file_name, file_size, chunk_size=1024*1024):
        """
        Initialize a file transfer.
        
        Args:
            file_id (str): Unique transfer identifier
            source (str): Source node ID
            target (str): Target node ID
            file_name (str): Name of the file being transferred
            file_size (int): Size of file in bytes
            chunk_size (int): Size of each chunk in bytes (default: 1MB)
        """
        self.file_id = file_id
        self.source = source
        self.target = target
        self.file_name = file_name
        self.file_size = file_size
        self.chunk_size = chunk_size
        self.total_chunks = math.ceil(file_size / chunk_size)
        self.transferred_chunks = 0
        self.completed = False
    
    def get_progress(self):
        """Get transfer progress percentage."""
        return (self.transferred_chunks / self.total_chunks) * 100


class StorageVirtualNetwork:
    """Manages a network of virtual storage nodes and file transfers."""
    
    def __init__(self):
        """Initialize an empty storage network."""
        self.nodes = {}
        self.connections = {}
        self.active_transfers = {}
        self.transfer_counter = 0
    
    def add_node(self, node):
        """Add a node to the network."""
        self.nodes[node.id] = node
    
    def connect_nodes(self, node1_id, node2_id, bandwidth):
        """Create a connection between two nodes."""
        key = f"{node1_id}-{node2_id}"
        self.connections[key] = {
            'bandwidth': bandwidth,
            'utilized': 0
        }
    
    def initiate_file_transfer(self, source_node_id, target_node_id, file_name, file_size):
        """
        Initiate a file transfer between two nodes.
        
        Args:
            source_node_id (str): Source node identifier
            target_node_id (str): Target node identifier
            file_name (str): Name of file to transfer
            file_size (int): Size of file in bytes
            
        Returns:
            FileTransfer: Transfer object if successful, None otherwise
        """
        source = self.nodes.get(source_node_id)
        target = self.nodes.get(target_node_id)
        
        if not source or not target:
            print(f"Error: Source or target node not found")
            return None
        
        if not target.allocate_storage(file_size):
            print(f"Error: Insufficient storage on {target_node_id}")
            return None
        
        file_id = f"transfer_{self.transfer_counter}"
        self.transfer_counter += 1
        
        transfer = FileTransfer(file_id, source_node_id, target_node_id, file_name, file_size)
        self.active_transfers[file_id] = transfer
        
        return transfer
    
    def process_file_transfer(self, source_node_id, target_node_id, file_id, chunks_per_step=1):
        """
        Process chunks of a file transfer.
        
        Args:
            source_node_id (str): Source node identifier
            target_node_id (str): Target node identifier
            file_id (str): Transfer identifier
            chunks_per_step (int): Number of chunks to process (default: 1)
            
        Returns:
            tuple: (chunks_processed, is_completed)
        """
        transfer = self.active_transfers.get(file_id)
        
        if not transfer or transfer.completed:
            return 0, True
        
        chunks_remaining = transfer.total_chunks - transfer.transferred_chunks
        chunks_to_process = min(chunks_per_step, chunks_remaining)
        
        transfer.transferred_chunks += chunks_to_process
        
        if transfer.transferred_chunks >= transfer.total_chunks:
            transfer.completed = True
        
        return chunks_to_process, transfer.completed
    
    def get_network_stats(self):
        """Get current network statistics."""
        total_bandwidth = sum(conn['bandwidth'] for conn in self.connections.values())
        active_count = sum(1 for t in self.active_transfers.values() if not t.completed)
        utilized = active_count * 100 if active_count > 0 else 0
        
        return {
            'bandwidth_utilization': (utilized / total_bandwidth * 100) if total_bandwidth > 0 else 0,
            'active_transfers': active_count,
            'total_transfers': len(self.active_transfers)
        }


# main.py
"""
Storage Virtual Network Simulator
Demonstrates file transfer simulation between virtual storage nodes.
"""

from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode

def main():
    """Main simulation function."""
    # Create network
    network = StorageVirtualNetwork()

    # Create nodes
    node1 = StorageVirtualNode("node1", cpu_capacity=4, memory_capacity=16, 
                               storage_capacity=500, bandwidth=1000)
    node2 = StorageVirtualNode("node2", cpu_capacity=8, memory_capacity=32, 
                               storage_capacity=1000, bandwidth=2000)

    # Add nodes to network
    network.add_node(node1)
    network.add_node(node2)

    # Connect nodes with 1Gbps link
    network.connect_nodes("node1", "node2", bandwidth=1000)

    # Initiate file transfer (100MB file from node1 to node2)
    transfer = network.initiate_file_transfer(
        source_node_id="node1",
        target_node_id="node2",
        file_name="large_dataset.zip",
        file_size=100 * 1024 * 1024  # 100MB
    )

    if transfer:
        print(f"Transfer initiated: {transfer.file_id}")
        
        # Process transfer in chunks
        while True:
            chunks_done, completed = network.process_file_transfer(
                source_node_id="node1",
                target_node_id="node2",
                file_id=transfer.file_id,
                chunks_per_step=3  # Process 3 chunks at a time
            )
            
            print(f"Transferred {chunks_done} chunks, completed: {completed}")
            
            if completed:
                print("Transfer completed successfully!")
                break
                
            # Get network stats
            stats = network.get_network_stats()
            print(f"Network utilization: {stats['bandwidth_utilization']:.2f}%")
            print(f"Storage utilization on node2: {node2.get_storage_utilization()['utilization_percent']:.2f}%")


if __name__ == "__main__":
    main()