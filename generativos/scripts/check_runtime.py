import json
import platform

import tensorflow as tf

print(
    json.dumps(
        {
            "python": platform.python_version(),
            "tensorflow": tf.__version__,
            "devices": [d.name for d in tf.config.list_physical_devices()],
            "gpu_optional": True,
        },
        indent=2,
    )
)
