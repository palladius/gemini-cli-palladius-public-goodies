
# Tests the python invocation


uv run ./generate_image.py \
    --prompt "Riccardo surfing in Milan at Idroscalo, wearing a python lang shirt" \
    --filename "test-ricc-python-milan.png" \
    -i "../assets/riccardo/ricc-google-switzerland.png" \
    -i "../assets/riccardo/ricc-pineapple-pizza.png" \
    -i "../assets/riccardo/riccardosouthafrica.png" \
    -i "../assets/riccardo/ricc-za-lake.png" \
    -i "../assets/riccardo/ricc-za-view-with-kids.png" \
    -i "../assets/riccardo/ricc-za-wine-tasting.png"
```