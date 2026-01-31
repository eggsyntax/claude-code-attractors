"""
Advanced Gradient Compression Utilities
Implements state-of-the-art compression techniques for federated learning.
Bob's Phase 2 implementation.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
import struct


@dataclass
class CompressionStats:
    """Statistics for compression operations."""
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    decompression_time: float
    error_metrics: Dict[str, float]


class BaseCompressor(ABC):
    """Abstract base class for gradient compression."""

    @abstractmethod
    def compress(self, data: np.ndarray) -> Tuple[Any, CompressionStats]:
        """Compress gradient data."""
        pass

    @abstractmethod
    def decompress(self, compressed_data: Any) -> np.ndarray:
        """Decompress gradient data."""
        pass


class QuantizationCompressor(BaseCompressor):
    """Advanced quantization-based compression with configurable bit widths."""

    def __init__(self,
                 bits: int = 8,
                 stochastic: bool = False,
                 scale_method: str = "minmax"):  # "minmax", "std", "dynamic"
        self.bits = bits
        self.stochastic = stochastic
        self.scale_method = scale_method
        self.levels = 2 ** bits - 1

    def compress(self, data: np.ndarray) -> Tuple[Dict[str, Any], CompressionStats]:
        """Compress using quantization."""
        import time
        start_time = time.time()

        original_shape = data.shape
        flat_data = data.flatten()

        # Calculate scale and offset based on method
        if self.scale_method == "minmax":
            data_min, data_max = float(np.min(flat_data)), float(np.max(flat_data))
            scale = (data_max - data_min) / self.levels if data_max > data_min else 1.0
            offset = data_min
        elif self.scale_method == "std":
            data_mean = float(np.mean(flat_data))
            data_std = float(np.std(flat_data))
            scale = 6 * data_std / self.levels  # Cover ±3σ
            offset = data_mean - 3 * data_std
        else:  # dynamic
            data_abs_max = float(np.max(np.abs(flat_data)))
            scale = 2 * data_abs_max / self.levels if data_abs_max > 0 else 1.0
            offset = -data_abs_max

        # Quantize
        if self.stochastic:
            # Stochastic quantization
            normalized = (flat_data - offset) / scale
            floor_vals = np.floor(normalized)
            prob = normalized - floor_vals
            random_bits = np.random.random(len(flat_data)) < prob
            quantized_vals = floor_vals + random_bits.astype(float)
        else:
            # Deterministic quantization
            quantized_vals = np.round((flat_data - offset) / scale)

        # Clip to valid range
        quantized_vals = np.clip(quantized_vals, 0, self.levels)

        # Convert to integers
        quantized_ints = quantized_vals.astype(np.uint32 if self.bits <= 32 else np.uint64)

        compression_time = time.time() - start_time

        # Pack into compressed format
        compressed_data = {
            'quantized_values': quantized_ints.tolist(),
            'scale': scale,
            'offset': offset,
            'shape': original_shape,
            'bits': self.bits,
            'method': self.scale_method
        }

        # Calculate compression statistics
        original_size = data.nbytes
        # Estimate compressed size (quantized values + metadata)
        compressed_size = (len(quantized_ints) * self.bits // 8 +
                          32)  # 32 bytes for metadata

        # Decompress for error calculation
        start_decomp = time.time()
        reconstructed = self.decompress(compressed_data)
        decompression_time = time.time() - start_decomp

        error_metrics = self._calculate_error_metrics(data, reconstructed)

        stats = CompressionStats(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compressed_size / original_size,
            compression_time=compression_time,
            decompression_time=decompression_time,
            error_metrics=error_metrics
        )

        return compressed_data, stats

    def decompress(self, compressed_data: Dict[str, Any]) -> np.ndarray:
        """Decompress quantized data."""
        quantized_ints = np.array(compressed_data['quantized_values'])
        scale = compressed_data['scale']
        offset = compressed_data['offset']
        shape = compressed_data['shape']

        # Reconstruct values
        reconstructed = quantized_ints.astype(np.float32) * scale + offset
        return reconstructed.reshape(shape)

    def _calculate_error_metrics(self, original: np.ndarray, reconstructed: np.ndarray) -> Dict[str, float]:
        """Calculate reconstruction error metrics."""
        mse = float(np.mean((original - reconstructed) ** 2))
        mae = float(np.mean(np.abs(original - reconstructed)))

        original_norm = np.linalg.norm(original)
        if original_norm > 0:
            relative_error = float(np.linalg.norm(original - reconstructed) / original_norm)
        else:
            relative_error = 0.0

        # Signal-to-noise ratio
        signal_power = float(np.mean(original ** 2))
        noise_power = float(np.mean((original - reconstructed) ** 2))
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float('inf')

        return {
            'mse': mse,
            'mae': mae,
            'relative_error': relative_error,
            'snr_db': snr
        }


class SparsificationCompressor(BaseCompressor):
    """Top-K and random sparsification compressor."""

    def __init__(self,
                 sparsity_ratio: float = 0.1,
                 method: str = "topk"):  # "topk", "random", "threshold"
        self.sparsity_ratio = sparsity_ratio
        self.method = method

    def compress(self, data: np.ndarray) -> Tuple[Dict[str, Any], CompressionStats]:
        """Compress using sparsification."""
        import time
        start_time = time.time()

        original_shape = data.shape
        flat_data = data.flatten()
        k = int(len(flat_data) * (1 - self.sparsity_ratio))

        if self.method == "topk":
            # Keep top-k largest magnitude elements
            indices = np.argpartition(np.abs(flat_data), -k)[-k:]
            values = flat_data[indices]
        elif self.method == "random":
            # Randomly sample k elements
            indices = np.random.choice(len(flat_data), k, replace=False)
            values = flat_data[indices]
        else:  # threshold
            # Keep elements above threshold
            threshold = np.percentile(np.abs(flat_data), self.sparsity_ratio * 100)
            mask = np.abs(flat_data) >= threshold
            indices = np.where(mask)[0]
            values = flat_data[indices]

        compression_time = time.time() - start_time

        compressed_data = {
            'indices': indices.tolist(),
            'values': values.tolist(),
            'shape': original_shape,
            'sparsity_ratio': self.sparsity_ratio,
            'method': self.method
        }

        # Calculate statistics
        original_size = data.nbytes
        # Indices (4 bytes each) + values (4 bytes each)
        compressed_size = len(indices) * 8 + 32  # 32 bytes metadata

        start_decomp = time.time()
        reconstructed = self.decompress(compressed_data)
        decompression_time = time.time() - start_decomp

        error_metrics = self._calculate_error_metrics(data, reconstructed)

        stats = CompressionStats(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compressed_size / original_size,
            compression_time=compression_time,
            decompression_time=decompression_time,
            error_metrics=error_metrics
        )

        return compressed_data, stats

    def decompress(self, compressed_data: Dict[str, Any]) -> np.ndarray:
        """Decompress sparse data."""
        indices = np.array(compressed_data['indices'])
        values = np.array(compressed_data['values'])
        shape = compressed_data['shape']

        # Reconstruct sparse array
        flat_reconstructed = np.zeros(np.prod(shape))
        flat_reconstructed[indices] = values
        return flat_reconstructed.reshape(shape)

    def _calculate_error_metrics(self, original: np.ndarray, reconstructed: np.ndarray) -> Dict[str, float]:
        """Calculate reconstruction error metrics."""
        mse = float(np.mean((original - reconstructed) ** 2))
        mae = float(np.mean(np.abs(original - reconstructed)))

        original_norm = np.linalg.norm(original)
        if original_norm > 0:
            relative_error = float(np.linalg.norm(original - reconstructed) / original_norm)
        else:
            relative_error = 0.0

        # Sparsity metrics
        sparsity_achieved = float(1 - np.count_nonzero(reconstructed) / reconstructed.size)

        return {
            'mse': mse,
            'mae': mae,
            'relative_error': relative_error,
            'sparsity_achieved': sparsity_achieved
        }


class HybridCompressor(BaseCompressor):
    """Hybrid compressor combining quantization and sparsification."""

    def __init__(self,
                 quantization_bits: int = 8,
                 sparsity_ratio: float = 0.1,
                 method: str = "sequential"):  # "sequential", "adaptive"
        self.quantizer = QuantizationCompressor(bits=quantization_bits)
        self.sparsifier = SparsificationCompressor(sparsity_ratio=sparsity_ratio)
        self.method = method

    def compress(self, data: np.ndarray) -> Tuple[Dict[str, Any], CompressionStats]:
        """Hybrid compression."""
        import time
        start_time = time.time()

        if self.method == "sequential":
            # Apply sparsification first, then quantization
            sparse_data, sparse_stats = self.sparsifier.compress(data)
            sparse_reconstructed = self.sparsifier.decompress(sparse_data)

            # Only quantize non-zero elements
            nonzero_mask = sparse_reconstructed != 0
            if np.any(nonzero_mask):
                nonzero_values = sparse_reconstructed[nonzero_mask]
                quant_data, quant_stats = self.quantizer.compress(nonzero_values)

                compressed_data = {
                    'sparse_data': sparse_data,
                    'quantized_data': quant_data,
                    'nonzero_mask': nonzero_mask.tolist(),
                    'method': 'sequential'
                }
            else:
                compressed_data = {
                    'sparse_data': sparse_data,
                    'method': 'sparse_only'
                }
                quant_stats = None

        else:  # adaptive
            # Choose best compression based on data characteristics
            sparse_data, sparse_stats = self.sparsifier.compress(data)
            quant_data, quant_stats = self.quantizer.compress(data)

            # Choose the one with better compression ratio
            if sparse_stats.compression_ratio < quant_stats.compression_ratio:
                compressed_data = {'sparse_data': sparse_data, 'method': 'sparse_only'}
                best_stats = sparse_stats
            else:
                compressed_data = {'quantized_data': quant_data, 'method': 'quant_only'}
                best_stats = quant_stats

        compression_time = time.time() - start_time

        # Calculate combined statistics
        start_decomp = time.time()
        reconstructed = self.decompress(compressed_data)
        decompression_time = time.time() - start_decomp

        error_metrics = self._calculate_error_metrics(data, reconstructed)

        # Estimate total compressed size
        if 'sparse_data' in compressed_data and 'quantized_data' in compressed_data:
            total_compressed_size = sparse_stats.compressed_size + quant_stats.compressed_size
        elif 'sparse_data' in compressed_data:
            total_compressed_size = sparse_stats.compressed_size
        else:
            total_compressed_size = quant_stats.compressed_size

        stats = CompressionStats(
            original_size=data.nbytes,
            compressed_size=total_compressed_size,
            compression_ratio=total_compressed_size / data.nbytes,
            compression_time=compression_time,
            decompression_time=decompression_time,
            error_metrics=error_metrics
        )

        return compressed_data, stats

    def decompress(self, compressed_data: Dict[str, Any]) -> np.ndarray:
        """Decompress hybrid data."""
        method = compressed_data['method']

        if method == 'sequential':
            # Reconstruct from sparse representation
            sparse_reconstructed = self.sparsifier.decompress(compressed_data['sparse_data'])

            if 'quantized_data' in compressed_data:
                # Apply quantization decompression to non-zero elements
                nonzero_mask = np.array(compressed_data['nonzero_mask'])
                quant_values = self.quantizer.decompress(compressed_data['quantized_data'])

                result = sparse_reconstructed.copy()
                result[nonzero_mask] = quant_values
                return result
            else:
                return sparse_reconstructed

        elif method == 'sparse_only':
            return self.sparsifier.decompress(compressed_data['sparse_data'])
        else:  # quant_only
            return self.quantizer.decompress(compressed_data['quantized_data'])

    def _calculate_error_metrics(self, original: np.ndarray, reconstructed: np.ndarray) -> Dict[str, float]:
        """Calculate reconstruction error metrics."""
        mse = float(np.mean((original - reconstructed) ** 2))
        mae = float(np.mean(np.abs(original - reconstructed)))

        original_norm = np.linalg.norm(original)
        if original_norm > 0:
            relative_error = float(np.linalg.norm(original - reconstructed) / original_norm)
        else:
            relative_error = 0.0

        return {
            'mse': mse,
            'mae': mae,
            'relative_error': relative_error
        }


class CompressionManager:
    """Manager for handling different compression algorithms and configurations."""

    def __init__(self):
        self.compressors = {}
        self.compression_history = []

    def register_compressor(self, name: str, compressor: BaseCompressor):
        """Register a new compressor."""
        self.compressors[name] = compressor

    def compress(self,
                 data: np.ndarray,
                 method: str = "quantization",
                 **kwargs) -> Tuple[Any, CompressionStats]:
        """Compress data using specified method."""
        if method == "quantization":
            compressor = QuantizationCompressor(**kwargs)
        elif method == "sparsification":
            compressor = SparsificationCompressor(**kwargs)
        elif method == "hybrid":
            compressor = HybridCompressor(**kwargs)
        elif method in self.compressors:
            compressor = self.compressors[method]
        else:
            raise ValueError(f"Unknown compression method: {method}")

        compressed_data, stats = compressor.compress(data)

        # Track compression history
        self.compression_history.append({
            'method': method,
            'stats': stats,
            'timestamp': time.time()
        })

        return compressed_data, stats

    def get_compression_summary(self) -> Dict[str, Any]:
        """Get summary of compression performance."""
        if not self.compression_history:
            return {'error': 'No compression history available'}

        recent_history = self.compression_history[-50:]  # Last 50 compressions

        methods_used = list(set(h['method'] for h in recent_history))

        summary = {
            'total_compressions': len(self.compression_history),
            'methods_used': methods_used,
            'recent_performance': {}
        }

        for method in methods_used:
            method_history = [h for h in recent_history if h['method'] == method]
            if method_history:
                stats = [h['stats'] for h in method_history]
                summary['recent_performance'][method] = {
                    'count': len(method_history),
                    'avg_compression_ratio': np.mean([s.compression_ratio for s in stats]),
                    'avg_compression_time': np.mean([s.compression_time for s in stats]),
                    'avg_relative_error': np.mean([s.error_metrics.get('relative_error', 0) for s in stats])
                }

        return summary