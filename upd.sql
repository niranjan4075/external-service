UPDATE peripherals
SET
  brand = CASE peripheral_id
    WHEN 46 THEN 'Kensington'
    WHEN 47 THEN 'Logitech'
    WHEN 48 THEN 'Apple'
    WHEN 37 THEN 'TBD'
    WHEN 33 THEN 'Dell'
    WHEN 34 THEN 'Apple'
    WHEN 35 THEN 'Apple'
    WHEN 36 THEN 'Kensington'
    WHEN 38 THEN 'Kensington'
    WHEN 39 THEN 'Apple'
    WHEN 41 THEN 'Jabra'
    WHEN 40 THEN 'Apple'
    WHEN 42 THEN 'Jabra'
    WHEN 43 THEN 'Kensington'
    WHEN 44 THEN 'Logitech'
    WHEN 45 THEN 'Apple'
  END,
  description = CASE peripheral_id
    WHEN 46 THEN 'Wired Mouse'
    WHEN 47 THEN 'Wireless Mouse'
    WHEN 48 THEN 'Wireless Mouse'
    WHEN 37 THEN 'Wireless Mouse'
    WHEN 33 THEN 'Docking Monitor'
    WHEN 34 THEN 'Wireless Headset'
    WHEN 35 THEN 'Wireless Keyboard'
    WHEN 36 THEN 'Wireless Keyboard'
    WHEN 38 THEN 'Laptop Privacy Screen'
    WHEN 39 THEN 'Tablet Stylus'
    WHEN 41 THEN 'Wireless Headset'
    WHEN 40 THEN 'Wireless Trackpad'
    WHEN 42 THEN 'Wireless Headset'
    WHEN 43 THEN 'Wired Keyboard'
    WHEN 44 THEN 'Wireless Keyboard/Mouse Combo'
    WHEN 45 THEN 'Wireless Mouse + Keyboard'
  END
WHERE peripheral_id IN (33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48);




INSERT INTO peripherals (
    peripheral_id,
    peripheral_type,
    peripheral_name,
    type_assignements,
    for_mac,
    is_current_standard,
    peripheral_image,
    brand,
    description
) VALUES (
    49, -- choose next available ID
    'Mouse',
    'Apple Magic Mouse Black',
    'Performance,Executive',
    true,
    true,
    NULL, -- or actual bytea image if available
    'Apple',
    'Wireless Mouse'
);
-- Insert Apple Magic Keyboard White
INSERT INTO peripherals (
    peripheral_id,
    peripheral_type,
    peripheral_name,
    type_assignements,
    for_mac,
    is_current_standard,
    peripheral_image,
    brand,
    description
) VALUES (
    50,
    'Keyboard',
    'Apple Magic Keyboard White',
    'Performance,Executive',
    true,
    true,
    NULL,
    'Apple',
    'Wireless Keyboard'
);

-- Insert Apple Magic Trackpad White
INSERT INTO peripherals (
    peripheral_id,
    peripheral_type,
    peripheral_name,
    type_assignements,
    for_mac,
    is_current_standard,
    peripheral_image,
    brand,
    description
) VALUES (
    51,
    'Magic Trackpad',
    'Apple Magic Trackpad White',
    'Performance,Executive',
    true,
    true,
    NULL,
    'Apple',
    'Wireless Trackpad'
);

