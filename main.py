import math

class FileTransfer:
    
    def _init_(self, file_id, source, target, file_name, file_size, chunk_size=1024*1024):
        self.file_id = file_id
        self.source = source
        self.target = target
        self.file_name = file_name
        self.file_size = file_size
        self.chunk_size = chunk_size
        self.total_chunks = max(1, math.ceil(file_size / chunk_size))
        self.transferred_chunks = 0
        self.completed = False
    
    def get_progress(self):
        return round(
            (self.transferred_chunks / self.total_chunks) * 100, 2
        )


class StorageVirtualNetwork:
    
    def _init_(self):
        self.nodes = {}
        self.connections = {}
        self.active_transfers = {}
        self.transfer_counter = 0
    
    def add_node(self, node):
        self.nodes[node.id] = node
    
    def connect_nodes(self, node1_id, node2_id, bandwidth):
        key = f"{node1_id}-{node2_id}"
        self.connections[key] = {
            'bandwidth': bandwidth,
            'utilized': 0
        }
    
    def initiate_file_transfer(self, source_node_id, target_node_id, file_name, file_size):
        source = self.nodes.get(source_node_id)
        target = self.nodes.get(target_node_id)
        
        if not source or not target:
            print("Error: Source or target node not found")
            return None
        
        if not target.allocate_storage(file_size):
            print(f"Error: Insufficient storage on {target_node_id}")
            return None
        
        file_id = f"transfer_{self.transfer_counter}"
        self.transfer_counter += 1
        
        transfer = FileTransfer(
            file_id, source_node_id, target_node_id, file_name, file_size
        )
        self.active_transfers[file_id] = transfer
        
        return transfer
    
    def process_file_transfer(self, source_node_id, target_node_id, file_id, chunks_per_step=1):
        transfer = self.active_transfers.get(file_id)
        
        if not transfer or transfer.completed:
            return 0, True
        
        remaining = transfer.total_chunks - transfer.transferred_chunks
        chunks = min(chunks_per_step, remaining)
        
        transfer.transferred_chunks += chunks
        
        if transfer.transferred_chunks >= transfer.total_chunks:
            transfer.completed = True
        
        return chunks, transfer.completed
    
    def get_network_stats(self):
        total_bandwidth = sum(c['bandwidth'] for c in self.connections.values())
        active_count = sum(1 for t in self.active_transfers.values() if not t.completed)
        
        return {
            'bandwidth_utilization': round(
                (active_count / total_bandwidth) * 100, 2
            ) if total_bandwidth else 0,
            'active_transfers': active_count,
            'total_transfers': len(self.active_transfers)
        }