# storage_node.py
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import time

class TransferStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ChunkInfo:
    chunk_id: str
    size: int
    status: TransferStatus
    timestamp: float

class FileTransfer:
    def __init__(self, file_id: str, file_name: str, file_size: int, 
                 source_node_id: str, chunk_size: int = 1024 * 1024):
        self.file_id = file_id
        self.file_name = file_name
        self.file_size = file_size
        self.source_node_id = source_node_id
        self.chunk_size = chunk_size
        self.status = TransferStatus.PENDING
        self.chunks: List[ChunkInfo] = []
        
        # Initialize chunks
        num_chunks = (file_size + chunk_size - 1) // chunk_size
        for idx in range(num_chunks):
            actual_chunk_size = min(chunk_size, file_size - idx * chunk_size)
            chunk = ChunkInfo(
                chunk_id=f"{file_id}_chunk_{idx}",
                size=actual_chunk_size,
                status=TransferStatus.PENDING,
                timestamp=time.time()
            )
            self.chunks.append(chunk)
    
    def get_progress(self) -> float:
        if not self.chunks:
            return 0.0
        completed_chunks = sum(1 for chunk in self.chunks if chunk.status == TransferStatus.COMPLETED)
        return (completed_chunks / len(self.chunks)) * 100

class StorageNode:
    def __init__(self, node_id: str, cpu_capacity: int, memory_capacity: int, 
                 storage_capacity: int, bandwidth: int):
        self.node_id = node_id
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.total_storage = storage_capacity
        self.bandwidth = bandwidth
        self.used_storage = 0
        self.network_utilization = 0
        self.connections: Dict[str, int] = {}
        self.active_transfers: Dict[str, FileTransfer] = {}
    
    def add_connection(self, target_node_id: str, bandwidth: int) -> None:
        self.connections[target_node_id] = bandwidth
    
    def allocate_storage(self, size: int) -> bool:
        if self.used_storage + size <= self.total_storage:
            self.used_storage += size
            return True
        return False
    
    def free_storage(self, size: int) -> None:
        self.used_storage = max(0, self.used_storage - size)
    
    def get_storage_utilization(self) -> Dict[str, float]:
        utilization_pct = (self.used_storage / self.total_storage) * 100 if self.total_storage > 0 else 0
        return {
            'used': self.used_storage,
            'capacity': self.total_storage,
            'utilization_percent': utilization_pct
        }
    
    def initiate_file_transfer(self, file_id: str, file_name: str, 
                              file_size: int, source_node_id: str) -> Optional[FileTransfer]:
        if not self.allocate_storage(file_size):
            return None
        
        transfer = FileTransfer(file_id, file_name, file_size, source_node_id)
        transfer.status = TransferStatus.IN_PROGRESS
        self.active_transfers[file_id] = transfer
        return transfer
    
    def process_chunk_transfer(self, file_id: str, chunk_id: str, 
                              source_node_id: str) -> bool:
        if file_id not in self.active_transfers:
            return False
        
        transfer = self.active_transfers[file_id]
        
        for chunk in transfer.chunks:
            if chunk.chunk_id == chunk_id and chunk.status != TransferStatus.COMPLETED:
                chunk.status = TransferStatus.COMPLETED
                chunk.timestamp = time.time()
                
                if all(c.status == TransferStatus.COMPLETED for c in transfer.chunks):
                    transfer.status = TransferStatus.COMPLETED
                
                return True
        
        return False


# storage_network.py
from typing import Dict, List, Optional, Tuple
import hashlib
import time
from storage_node import StorageNode, FileTransfer, TransferStatus # type: ignore
from collections import defaultdict

class StorageNetwork:
    def __init__(self):
        self.nodes: Dict[str, StorageNode] = {}
        self.transfer_operations: Dict[str, Dict[str, FileTransfer]] = defaultdict(dict)
        
    def add_node(self, node: StorageNode):
        self.nodes[node.node_id] = node
        
    def connect_nodes(self, node1_id: str, node2_id: str, bandwidth: int):
        if node1_id in self.nodes and node2_id in self.nodes:
            self.nodes[node1_id].add_connection(node2_id, bandwidth)
            self.nodes[node2_id].add_connection(node1_id, bandwidth)
            return True
        return False
    
    def initiate_file_transfer(
        self,
        source_node_id: str,
        target_node_id: str,
        file_name: str,
        file_size: int
    ) -> Optional[FileTransfer]:
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            return None
            
        file_id = hashlib.md5(f"{file_name}-{time.time()}".encode()).hexdigest()
        
        target_node = self.nodes[target_node_id]
        transfer = target_node.initiate_file_transfer(file_id, file_name, file_size, source_node_id)
        
        if transfer:
            self.transfer_operations[source_node_id][file_id] = transfer
            return transfer
        return None
    
    def process_file_transfer(
        self,
        source_node_id: str,
        target_node_id: str,
        file_id: str,
        chunks_per_step: int = 1
    ) -> Tuple[int, bool]:
        if (source_node_id not in self.nodes or 
            target_node_id not in self.nodes or
            file_id not in self.transfer_operations[source_node_id]):
            return (0, False)
            
        source_node = self.nodes[source_node_id]
        target_node = self.nodes[target_node_id]
        transfer = self.transfer_operations[source_node_id][file_id]
        
        chunks_transferred = 0
        for chunk in transfer.chunks:
            if chunk.status != TransferStatus.COMPLETED and chunks_transferred < chunks_per_step:
                if target_node.process_chunk_transfer(file_id, chunk.chunk_id, source_node_id):
                    chunks_transferred += 1
                else:
                    return (chunks_transferred, False)
        
        if transfer.status == TransferStatus.COMPLETED:
            del self.transfer_operations[source_node_id][file_id]
            return (chunks_transferred, True)
            
        return (chunks_transferred, False)
    
    def get_network_stats(self) -> Dict[str, float]:
        total_bandwidth = sum(n.bandwidth for n in self.nodes.values())
        used_bandwidth = sum(n.network_utilization for n in self.nodes.values())
        total_storage = sum(n.total_storage for n in self.nodes.values())
        used_storage = sum(n.used_storage for n in self.nodes.values())
        
        bandwidth_util = (used_bandwidth / total_bandwidth) * 100 if total_bandwidth > 0 else 0
        storage_util = (used_storage / total_storage) * 100 if total_storage > 0 else 0
        
        return {
            "total_nodes": len(self.nodes),
            "total_bandwidth_bps": total_bandwidth,
            "used_bandwidth_bps": used_bandwidth,
            "bandwidth_utilization": bandwidth_util,
            "total_storage_bytes": total_storage,
            "used_storage_bytes": used_storage,
            "storage_utilization": storage_util,
            "active_transfers": sum(len(t) for t in self.transfer_operations.values())
        }


# main.py
from storage_network import StorageNetwork # type: ignore
from storage_node import StorageNode # type: ignore

# Initialize network
network = StorageNetwork()

# Setup nodes
node1 = StorageNode("node1", cpu_capacity=4, memory_capacity=16, 
                    storage_capacity=500 * 1024 * 1024, bandwidth=1000000000)
node2 = StorageNode("node2", cpu_capacity=8, memory_capacity=32, 
                    storage_capacity=1000 * 1024 * 1024, bandwidth=2000000000)

network.add_node(node1)
network.add_node(node2)

# Establish connection
network.connect_nodes("node1", "node2", bandwidth=1000000000)

# Start file transfer
transfer = network.initiate_file_transfer(
    source_node_id="node1",
    target_node_id="node2",
    file_name="large_dataset.zip",
    file_size=100 * 1024 * 1024
)

if transfer:
    print(f"Transfer initiated: {transfer.file_id}")
    
    # Process transfer
    while True:
        chunks_done, completed = network.process_file_transfer(
            source_node_id="node1",
            target_node_id="node2",
            file_id=transfer.file_id,
            chunks_per_step=3
        )
        
        print(f"Transferred {chunks_done} chunks, completed: {completed}")
        
        if completed:
            print("Transfer completed successfully!")
            break
            
        stats = network.get_network_stats()
        print(f"Network utilization: {stats['bandwidth_utilization']:.2f}%")
        print(f"Storage utilization on node2: {node2.get_storage_utilization()['utilization_percent']:.2f}%")