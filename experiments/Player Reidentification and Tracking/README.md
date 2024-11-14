The experiments were done in testing_claims.ipynb. These exiperiments werenot able to be transferred or deployed into the model due to its high time consumption.

There would be some modifications done in this folder depending on time available.

Possible Modifications:
1. Instead of using VitPose to find the crop area for further search, train a small YOLO model to find the crop region with numbers in the jersey to find the region with high confidence. This requires finding good dataset and training the model on this.
2. Depends on the architecture of VitPose, one can choose to quantize it and try to decrease the inference time within this. or train the VitPose model from scratch.