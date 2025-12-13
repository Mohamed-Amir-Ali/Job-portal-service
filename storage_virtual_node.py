import time
import math
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from enum import Enum, auto

class TransferStatus(Enum):
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()

@dataclass
class FileChunk:
    chunk_id: int
    size: int
    checksum: str
    status: TransferStatus = TransferStatus.PENDING
    stored_node: Optional[str] = None

@dataclass
class FileTransfer:
    file_id: str
    file_name: str
    total_size: int
    chunks: List[FileChunk]
    status: TransferStatus = TransferStatus.PENDING
    created_at: float = time.time()
    completed_at: Optional[float] = None

class StorageVirtualNode:
    def _init_(
        self,
        node_id: str,
        cpu_capacity: int,
        memory_capacity: int,
        storage_capacity: int,
        bandwidth: int
    ):
        self.node_id = node_id
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.total_storage = storage_capacity * 1024 * 1024 * 1024
        self.bandwidth = bandwidth * 1_000_000

        # Track resources
        self.used_storage = 0
        self.active_transfers: Dict[str, FileTransfer] = {}
        self.stored_files: Dict[str, FileTransfer] = {}
        self.network_utilization = 0

        # Statistics
        self.total_requests_processed = 0
        self.total_data_transferred = 0
        self.failed_transfers = 0

        # Connections to other nodes
        self.connections: Dict[str, int] = {}

    def add_connection(self, node_id: str, bandwidth: int):
        """Link this node to another node with a given bandwidth (Mbps)."""
        self.connections[node_id] = bandwidth * 1_000_000

    def _determine_chunk_size(self, file_size: int) -> int:
        """Select optimal chunk size based on file size."""
        if file_size < 10 * 1024 * 1024:
            return 512 * 1024
        elif file_size < 100 * 1024 * 1024:
            return 2 * 1024 * 1024
        else:
            return 10 * 1024 * 1024

    def _split_into_chunks(self, file_id: str, file_size: int) -> List[FileChunk]:
        """Divide the file into chunks with checksums."""
        chunk_size = self._determine_chunk_size(file_size)
        num_chunks = math.ceil(file_size / chunk_size)
        chunks: List[FileChunk] = []

        for idx in range(num_chunks):
            checksum = hashlib.md5(f"{file_id}-{idx}".encode()).hexdigest()
            actual_size = min(chunk_size, file_size - idx * chunk_size)
            chunks.append(FileChunk(
                chunk_id=idx,
                size=actual_size,
                checksum=checksum
            ))
        return chunks

    def initiate_file_transfer(
        self,
        file_id: str,
        file_name: str,
        file_size: int,
        source_node: Optional[str] = None
    ) -> Optional[FileTransfer]:
        """Start a new file transfer on this node."""
        if self.used_storage + file_size > self.total_storage:
            return None

        chunks = self._split_into_chunks(file_id, file_size)
        transfer = FileTransfer(
            file_id=file_id,
            file_name=file_name,
            total_size=file_size,
            chunks=chunks
        )
        self.active_transfers[file_id] = transfer
        return transfer

    def process_chunk_transfer(self, file_id: str, chunk_id: int, source_node: str) -> bool:
        """Receive and store a single file chunk from a source node."""
        if file_id not in self.active_transfers:
            return False

        transfer = self.active_transfers[file_id]
        chunk = next((c for c in transfer.chunks if c.chunk_id == chunk_id), None)
        if not chunk:
            return False

        chunk_bits = chunk.size * 8
        available_bw = min(
            self.bandwidth - self.network_utilization,
            self.connections.get(source_node, 0)
        )

        if available_bw <= 0:
            return False

        # Simulate transfer duration
        time.sleep(chunk_bits / available_bw)

        chunk.status = TransferStatus.COMPLETED
        chunk.stored_node = self.node_id

        self.network_utilization += available_bw * 0.8
        self.total_data_transferred += chunk.size

        # Check if file transfer is complete
        if all(c.status == TransferStatus.COMPLETED for c in transfer.chunks):
            transfer.status = TransferStatus.COMPLETED
            transfer.completed_at = time.time()
            self.used_storage += transfer.total_size
            self.stored_files[file_id] = transfer
            del self.active_transfers[file_id]
            self.total_requests_processed += 1

        return True

    def retrieve_file(self, file_id: str, destination_node: str) -> Optional[FileTransfer]:
        """Create a copy of a stored file for retrieval to another node."""
        if file_id not in self.stored_files:
            return None

        stored = self.stored_files[file_id]
        new_transfer = FileTransfer(
            file_id=f"retr-{file_id}-{time.time()}",
            file_name=stored.file_name,
            total_size=stored.total_size,
            chunks=[
                FileChunk(
                    chunk_id=c.chunk_id,
                    size=c.size,
                    checksum=c.checksum,
                    stored_node=destination_node
                ) for c in stored.chunks
            ]
        )
        return new_transfer

    def get_storage_utilization(self) -> Dict[str, Union[int, float]]:
        """Return current storage usage statistics."""
        return {
            "used_bytes": self.used_storage,
            "total_bytes": self.total_storage,
            "utilization_percent": (self.used_storage / self.total_storage) * 100,
            "files_stored": len(self.stored_files),
            "active_transfers": len(self.active_transfers)
        }

    def get_network_utilization(self) -> Dict[str, Union[int, float, List[str]]]:
        """Return current network utilization statistics."""
        return {
            "current_utilization_bps": self.network_utilization,
            "max_bandwidth_bps": self.bandwidth,
            "utilization_percent": (self.network_utilization / self.bandwidth) * 100,
            "connections": list(self.connections.keys())
        }

    def get_performance_metrics(self) -> Dict[str, int]:
        """Return overall node performance metrics."""
        return {
            "total_requests_processed": self.total_requests_processed,
            "total_data_transferred_bytes": self.total_data_transferred,
            "failed_transfers": self.failed_transfers,
            "current_active_transfers": len(self.active_transfers)
        }