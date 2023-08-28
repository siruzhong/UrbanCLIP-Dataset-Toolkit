# 数据增强工具

这个工具旨在对四个城市的图像和相关的文本数据进行数据增强。

## 主要功能

- **图像增强**：取两张图像进行线性混合。
- **文本增强**：将两段文本简单串联。
- **ID生成**：对于每对增强的数据，产生一个新的ID作为标识。

## 使用步骤

1. **设置路径**：

   - `data_paths`: 输入的原始数据JSON文件路径。
   - `output_directories`: 输出的增强图像目录。
   - `output_json_paths`: 输出的增强数据JSON文件路径。

2. **运行脚本**：脚本会处理每个城市的数据，并输出增强后的图像和JSON文件。

3. **检查输出**：

   - 增强的图像保存在指定的目录中。
   - 每个城市的增强数据（包括图像路径、文本和新ID）保存在对应的JSON文件中。

## 注意事项

- 确保输入的JSON文件格式正确，应包含图像路径、文本描述和ID。
- 为了成功进行数据增强，每个城市的数据集大小应为偶数。
- 图像在处理时会被归一化到[0, 1]范围。