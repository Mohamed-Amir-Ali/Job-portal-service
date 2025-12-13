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
    id: str
    size: int
    status: TransferStatus
    timestamp: float

class FileTransfer:
    def _init_(self, file_id: str, name: str, size: int, 
                 source_node: str, chunk_size: int = 1024*1024):
        self.file_id = file_id
        self.name = name
        self.size = size
        self.source_node = source_node
        self.chunk_size = chunk_size
        self.status = TransferStatus.PENDING
        self.chunks: List[ChunkInfo] = []

        total_chunks = (size + chunk_size - 1) // chunk_size
        for idx in range(total_chunks):
            this_chunk_size = min(chunk_size, size - idx * chunk_size)
            self.chunks.append(ChunkInfo(
                id=f"{file_id}chunk{idx}",
                size=this_chunk_size,
                status=TransferStatus.PENDING,
                timestamp=time.time()
            ))

    def progress_percentage(self) -> float:
        if not self.chunks:
            return 0.0
        finished = sum(1 for c in self.chunks if c.status == TransferStatus.COMPLETED)
        return (finished / len(self.chunks)) * 100

class StorageNode:
    def _init_(self, node_id: str, cpu: int, memory: int, storage: int, bandwidth: int):
        self.node_id = node_id
        self.cpu_capacity = cpu
        self.memory_capacity = memory
        self.total_storage = storage
        self.bandwidth = bandwidth
        self.used_storage = 0
        self.network_utilization = 0
        self.connections: Dict[str, int] = {}
        self.active_transfers: Dict[str, FileTransfer] = {}

    def connect_to(self, other_node_id: str, bandwidth: int):
        self.connections[other_node_id] = bandwidth

    def reserve_storage(self, size: int) -> bool:
        if self.used_storage + size <= self.total_storage:
            self.used_storage += size
            return True
        return False

    def release_storage(self, size: int):
        self.used_storage = max(0, self.used_storage - size)

    def storage_utilization(self) -> Dict[str, float]:
        percent = (self.used_storage / self.total_storage) * 100 if self.total_storage > 0 else 0
        return {"used": self.used_storage, "capacity": self.total_storage, "utilization_percent": percent}

    def start_transfer(self, file_id: str, name: str, size: int, source_node: str) -> Optional[FileTransfer]:
        if not self.reserve_storage(size):
            return None
        transfer = FileTransfer(file_id, name, size, source_node)
        transfer.status = TransferStatus.IN_PROGRESS
        self.active_transfers[file_id] = transfer
        return transfer

    def process_chunk(self, file_id: str, chunk_id: str, source_node: str) -> bool:
        if file_id not in self.active_transfers:
            return False
        transfer = self.active_transfers[file_id]
        for chunk in transfer.chunks:
            if chunk.id == chunk_id and chunk.status != TransferStatus.COMPLETED:
                chunk.status = TransferStatus.COMPLETED
                chunk.timestamp = time.time()
                if all(c.status == TransferStatus.COMPLETED for c in transfer.chunks):
                    transfer.status = TransferStatus.COMPLETED
                return True
        return False


from typing import Dict, Optional, Tuple
import hashlib
import time
from storage_node import StorageNode, FileTransfer, TransferStatus
from collections import defaultdict

class StorageNetwork:
    def _init_(self):
        self.nodes: Dict[str, StorageNode] = {}
        self.transfers: Dict[str, Dict[str, FileTransfer]] = defaultdict(dict)

    def add_node(self, node: StorageNode):
        self.nodes[node.node_id] = node

    def link_nodes(self, node1: str, node2: str, bandwidth: int) -> bool:
        if node1 in self.nodes and node2 in self.nodes:
            self.nodes[node1].connect_to(node2, bandwidth)
            self.nodes[node2].connect_to(node1, bandwidth)
            return True
        return False

    def start_file_transfer(self, source_node: str, target_node: str, name: str, size: int) -> Optional[FileTransfer]:
        if source_node not in self.nodes or target_node not in self.nodes:
            return None
        file_id = hashlib.md5(f"{name}-{time.time()}".encode()).hexdigest()
        transfer = self.nodes[target_node].start_transfer(file_id, name, size, source_node)
        if transfer:
            self.transfers[source_node][file_id] = transfer
            return transfer
        return None

    def transfer_chunks(self, source_node: str, target_node: str, file_id: str, chunks_step: int = 1) -> Tuple[int, bool]:
        if (source_node not in self.nodes or target_node not in self.nodes or
            file_id not in self.transfers[source_node]):
            return 0, False

        target = self.nodes[target_node]
        transfer = self.transfers[source_node][file_id]
        transferred = 0

        for chunk in transfer.chunks:
            if chunk.status != TransferStatus.COMPLETED and transferred < chunks_step:
                if target.process_chunk(file_id, chunk.id, source_node):
                    transferred += 1
                else:
                    return transferred, False

        done = transfer.status == TransferStatus.COMPLETED
        if done:
            del self.transfers[source_node][file_id]
        return transferred, done

    def network_statistics(self) -> Dict[str, float]:
        total_bw = sum(n.bandwidth for n in self.nodes.values())
        used_bw = sum(n.network_utilization for n in self.nodes.values())
        total_storage = sum(n.total_storage for n in self.nodes.values())
        used_storage = sum(n.used_storage for n in self.nodes.values())
        return {
            "total_nodes": len(self.nodes),
            "total_bandwidth_bps": total_bw,
            "used_bandwidth_bps": used_bw,
            "bandwidth_utilization": (used_bw/total_bw*100) if total_bw else 0,
            "total_storage_bytes": total_storage,
            "used_storage_bytes": used_storage,
            "storage_utilization": (used_storage/total_storage*100) if total_storage else 0,
            "active_transfers": sum(len(t) for t in self.transfers.values())
        }


from storage_network import StorageNetwork
from storage_node import StorageNode

network = StorageNetwork()

node1 = StorageNode("node1", cpu=4, memory=16, storage=500*1024*1024, bandwidth=1_000_000_000)
node2 = StorageNode("node2", cpu=8, memory=32, storage=1_000*1024*1024, bandwidth=2_000_000_000)

network.add_node(node1)
network.add_node(node2)
network.link_nodes("node1", "node2", bandwidth=1_000_000_000)

transfer = network.start_file_transfer("node1", "node2", "large_dataset.zip", 100*1024*1024)

if transfer:
    print(f"Transfer started: {transfer.file_id}")
    while True:
        done_chunks, finished = network.transfer_chunks("node1", "node2", transfer.file_id, chunks_step=3)
        print(f"Transferred {done_chunks} chunks, completed: {finished}")
        if finished:
            print("File transfer successfully completed!")
            break
        stats = network.network_statistics()
        print(f"Network usage: {stats['bandwidth_utilization']:.2f}%")
        print(f"Node2 storage usage: {node2.storage_utilization()['utilization_percent']:.2f}%")