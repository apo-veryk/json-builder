import csv
import json
from bson import ObjectId
from collections import defaultdict
import random
import os

# tracking already generated IDs within this script execution
generated_ids = set()

def custom_json_encoder(obj):
    """Convert ObjectIds to strings for JSON output."""
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

# assuming you have a global set and generate_random_id function:
generated_ids = set()

def generate_random_id():
    hex_chars = "0123456789abcdef"
    while True: 
        first_chars = 'ID'
        suffix = ''.join(random.choice(hex_chars) for _ in range(23))
        new_id = first_chars + suffix
        if new_id not in generated_ids:  # ensuring that is **not** unique
            generated_ids.add(new_id) 
            return new_id  

def cats_gen(items_csv_path):
    """
    Reads items.csv to find all unique cat_name has something something.
    Then builds a 'catalog' dictionary has something something, including:
      - Main categories
      - Subcategories (and a 'Misc' if needed)
      - Linking parent/child IDs
      - A random ID for the catalog $oid
      - next_category_local_id, primary_language, etc.
    Returns a dictionary that you can later insert into your final JSON.
    """

    cat_subcat_pairs = set()

    with open(items_csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat_name = row.get("cat_name", "").strip()
            sub_cat = row.get("sub_cat", "").strip()
            if cat_name:  
                cat_subcat_pairs.add((cat_name, sub_cat))

    #$oid and top-level fields
    cata_id = generate_random_id()  # random ID for the catalog itself

    cata_obj = {
        "$oid": {"_id": cata_id},
        "categories": [],
        "......": [],
        "......": [],
        "......": [],
        "......": [],
        "......": [],
        "v": {
            "author": {
                "id": "60a28b421f64e098f8e21493",
                "kind": "user"
            },
            "created_at": {
                "$date": 1739358269656
            },
            "is_removed": False,
            "......": [],
            "......": [],
            "......": [],
            "......": [],
            "......": [],
            "orig_id": {
                "_id": cata_id
            }
        }
    }
    from collections import defaultdict
    cats_to_subcats = defaultdict(set)
    for (c, sc) in cat_subcat_pairs:
        cats_to_subcats[c].add(sc)
    cat_id_map = {}
    cat_name_map = {}
    main_cats_map = {}
    subcat_map = {}
    local_id_counter = 0
    for c_name, subcats in cats_to_subcats.items():
        # random ID for the main category
        cat_oid = generate_random_id()
        main_cat_obj = {
            "child_category_ids": [],
            "description": [],
            "id": {"_id": cat_oid},
            "image": "",
            "image_blur": "",
            "items": [], 
            "local": local_id_counter,
            "name": [
                {
                    "lang": "el",
                    "value": c_name, 
                    "verified": True
                }
            ]
        }
        local_id_counter += 1
        main_cats_map[c_name] = main_cat_obj
        cata_obj["categories"].append(main_cat_obj)
        real_subcats = {s for s in subcats if s}

        if not real_subcats:
            # means it has NO subcategories. later items will go here
            # in main_cat_obj["items"].
            pass
        else:
            for sc_name in real_subcats:
                sc_oid = generate_random_id()
                sc_obj = {
                    "child_category_ids": [],
                    "description": [],
                    "id": {"_id": sc_oid},
                    "image": "",
                    "image_blur": "",
                    "......": [],
                    "......": [],
                    "......": [],
                    "......": [],
                    "......": [],
                    "local": local_id_counter,
                    "name": [
                        {
                            "lang": "el",
                            "value": sc_name,
                            "verified": True
                        }
                    ],
                    "parent_category_id": {"_id": cat_oid}
                }
                local_id_counter += 1
                main_cat_obj["child_category_ids"].append({"_id": sc_oid})
                subcat_map[(c_name, sc_name)] = sc_obj
                cata_obj["categories"].append(sc_obj)

            if "" in subcats:
                misc_oid = generate_random_id()
                misc_obj = {
                    "child_category_ids": [],
                    "......": [],
                    "......": [],
                    "......": [],
                    "......": [],
                    "......": [],
                    "id": {"_id": misc_oid},
                    "image": "",
                    "image_blur": "",
                    "items": [],
                    "local": local_id_counter,
                    "name": [
                        {
                            "lang": "el",
                            "value": "Misc",
                            "verified": True
                        }
                    ],
                    "parent_category_id": {"_id": cat_oid}
                }
                local_id_counter += 1
                main_cat_obj["child_category_ids"].append({"_id": misc_oid})
                subcat_map[(c_name, "Misc")] = misc_obj
                cata_obj["categories"].append(misc_obj)
                print(f"📌 Created 'Misc' subcategory for '{c_name}' to store unclassified items.")

    cat_map = {}
    for c_name, cat_obj in main_cats_map.items():
        cat_map[(c_name, "")] = cat_obj
    for (c_name, sc_name), sc_obj in subcat_map.items():
        cat_map[(c_name, sc_name)] = sc_obj

    return cata_obj, cat_map

def opts_gen(options_csv_path, cata_id):
    """
    Reads options.csv which MUST have columns: an identifier and 'opt_name'.
    Groups rows by (merchant_sku, dis_name) => each group => 1 "option combination".
    Then each row in that group => 1 "value".

    If dis_name is empty, we default it to "Επίλεξε νούμερο".
    If ext_id, price_markup, etc. exist, we store them as well.
    """

    import csv
    from collections import defaultdict
    combo_map = defaultdict(list)
    with open(options_csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        required_cols = ["merchant_sku", "opt_name"]
        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"ERROR: has something something have column '{col}'.")
        for row in reader:
            merchant_sku = row["merchant_sku"].strip()
            opt_name = row["opt_name"].strip()
            if not merchant_sku:
                print("Warning: has something something. Skipping.")
                continue
            if not opt_name:
                print(f"Warning: row for merchant_sku=........' has something something name. Skipping.")
                continue
            dis_name = row.get("dis_name", "").strip()
            if not dis_name:
                dis_name = "Επίλεξε νούμερο"
            combo_map[(merchant_sku, dis_name)].append(row)

    final_options = []

    for (merchant_sku, dis_name), row_list in combo_map.items():
        combo_id = generate_random_id()

        option_obj = {
            "$oid": {"_id": combo_id},
            "default_value": None,
            "......": [],
            "......": [],
            "......": [],
            "......": [],
            "......": [],
            "cata_id": {"_id": cata_id},
            "name": [
                {
                    "lang": "el",
                    "value": dis_name,      
                    "verified": True
                }
            ],
            "type": "choice",

            "v": {
                "author": {
                    "id": "60a28b421f64e098f8e21493",
                    "kind": "user"
                },
                "created_at": {"$date": 1739358269656},
                "is_removed": False,
                "num": 999,
                "orig_id": {"_id": combo_id}
            },

            "values": []
        }
        first_value_oid = None
        for i, row_data in enumerate(row_list):
            val_id = generate_random_id()
            opt_name = row_data["opt_name"].strip()
            ext_id = row_data.get("ext_id", "").strip()
            price_markup_str = row_data.get("price_markup", "").strip()

            value_obj = {
                "id": {"_id": val_id},
                "......": [],
                "......": [],
                "......": [],
                "......": [],
                "......": [],
                "conditions_of_use_and_storage": [],
                "country": [],
                "dietary_preferences": [],
                "distributor_information": [],
                "......": [],
                "ingredients": [],
                "mandatory_warnings": [],
                "name": [
                    {
                        "lang": "el",
                        "value": opt_name,
                        "verified": True
                    }
                ],
                "nutrition_facts": [],
                "producer_information": [],
                "regulatory_information": [],
                "......": [],
                "......": [],
                "......": [],
                "......": [],
                "......": []
            }
            if price_markup_str:
                try:
                    price_markup_int = int(price_markup_str)
                    value_obj["price_markup"] = price_markup_int
                except ValueError:
                    print(f"Warning: price_markup='{price_markup_str}' is an integer. Skipping.")

            if i == 0:
                first_value_oid = val_id
            option_obj["values"].append(value_obj)

        if first_value_oid:
            option_obj["default_value"] = {"_id": first_value_oid}

        final_options.append(option_obj)

    return final_options

def items_gen(items_csv_path, cata_id, options_list, cat_map, sku_to_images):
    """
    Reads items.csv and produces a list of item objects in the desired JSON structure. MANDATORY AND NON-MANDATORY FIELDS__
    - 'producer_information': If present and non-empty => array of localized objects with lang='el'.
    - 'enabled': Must be 'YES' or 'NO' if present => sets item_doc["enabled"].
    - 'in_stock': Must be 'Y' or 'N' if present => 'N' => item_doc["inventory_mode"]='forced_out_of_stock',
      'Y' => omit the attribute, else error.
    - 'more_information': if present => array of localized objects with lang='el'.
    """

    externalid_to_option = {}
    for opt_doc in options_list:
        key = opt_doc.get("external_id", "")
        if key:
            externalid_to_option[key] = opt_doc

    items = []
    
    with open(items_csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        required_cols = ["price", "name", "cat_name"]
        for col in required_cols:
            if col not in fieldnames:
                raise ValueError(f"ERROR: items.csv has a .....'{col}'")

        has_more_info = "more_information" in fieldnames
        has_producer_info = "producer_information" in fieldnames
        has_enabled_col = "enabled" in fieldnames
        has_in_stock_col = "in_stock" in fieldnames
        has_description = "description" in fieldnames
        has_brand_id = "brand_id" in fieldnames
        
        for row_index, row in enumerate(reader, start=1):
            price_str = row.get("price", "").strip()
            name_str = row.get("name", "").strip()
            cat_name_str = row.get("cat_name", "").strip()

            if not price_str or not name_str or not cat_name_str:
                print(f"ERROR at row {row_index}:..........")
                raise ValueError("columns may be empty.......... Aborting.")

            sub_cat_str = row.get("sub_cat", "").strip()
            item_id = generate_random_id()

            try:
                price_float = float(price_str)
            except ValueError:
                print(f"ERROR: price='{price_str}' is not a number (row {row_index}).")
                raise
            baseprice = int(round(price_float * 100))

            item_doc = {
                "$oid": {"_id": item_id},
                "additives": [],
                "alcohol_percentage": 0,
                "allergens": [],
                "baseprice": baseprice,
                "color": [],
                "conditions_of_use_and_storage": [],
                "country": [],
                "courier_restrictions": [],
                "delivery_methods": [],
                "description": [],
                "dietary_preferences": [],
                "unit_type": "single_unit",
                "number_of_units": 1,
                "distributor_information": [],
                "enabled": {"enabled": True},  # default = True
                "external_id": row.get("external_id", "").strip(),
                "image": row.get("image", "").strip(),
                "image_blur": row.get("image_blur", "").strip(),
                "images": [],
                "ingredients": [],
                "is_bundle_offer": False,
                "is_over_the_counter": False,
                "mandatory_warnings": [],
                "cata_id": {"_id": cata_id},
                "merchant_sku": row.get("merchant_sku", "").strip(),
                "more_information": [],
                "name": [
                    {
                        "lang": "el",
                        "value": name_str,
                        "verified": True
                    }
                ],
                "nutrition_facts": [],
                "nutrition_values": [],
                "offering_platform_metadata": {
                    "id": {"_id": generate_random_id()}
                },
                "options": [],
                "producer_information": [],  # default empty
                "regulatory_information": [],
                "size": [],
                "user_requirements": [],
                "v": {
                    "author": {
                        "id": "60a28b421f64e098f8e21493",
                        "kind": "user"
                    },
                    "created_at": {"$date": 1739358269656},
                    "is_removed": False,
                    "num": 999,
                    "orig_id": {"_id": item_id}
                }
            }
            if has_brand_id:
                brand_val = row["brand_id"].strip()
                if brand_val:
                    item_doc["brand_id"] = brand_val
            if has_description:
                desc_val = row["description"].strip()
                if desc_val:
                    item_doc["description"] = [
                        {
                            "lang": "el",
                            "value": desc_val,
                            "verified": True
                        }
                    ]
            if has_more_info:
                more_info_val = row["more_information"].strip()
                if more_info_val:
                    item_doc["more_information"] = [
                        {
                            "lang": "el",
                            "value": more_info_val,
                            "verified": True
                        }
                    ]
            if has_producer_info:
                producer_val = row["producer_information"].strip()
                if producer_val:
                    item_doc["producer_information"] = [
                        {
                            "lang": "el",
                            "value": producer_val,
                            "verified": True
                        }
                    ]
            if has_enabled_col:
                enabled_val = row["enabled"].strip().upper()  #  'YES' or 'NO'
                if enabled_val:
                    if enabled_val == "YES":
                        item_doc["enabled"] = {"enabled": True}
                    elif enabled_val == "NO":
                        item_doc["enabled"] = {"enabled": False}
                    else:
                        raise ValueError(f"Invalid 'enabled' value '{enabled_val}' at row {row_index}. "
                                         f"Must be 'YES' or 'NO'.")
                # if blank, we do nothing (default True)

            item_doc["inventory_mode"] = ""

            dm_val = row.get("delivery_methods", "").strip()
            if dm_val:
                item_doc["delivery_methods"] = [
                    x.strip() for x in dm_val.split(",") if x.strip()
                ]
            else:
                item_doc["delivery_methods"] = ["eatin","takeaway","homedelivery"]
            desc_val = row.get("description", "").strip()
            if desc_val:
                item_doc["description"] = [
                    {
                        "lang": "el",
                        "value": desc_val,
                        "verified": True
                    }
                ]
            else:
                item_doc["description"] = [
                    {
                        "lang": "el",
                        "value": "",
                        "verified": True
                    }
                ]
            item_doc["image_blur"] = row.get("image_blur", "").strip()
            merchant_sku = row.get("merchant_sku", "").strip()
            extra_images = sku_to_images.get(merchant_sku, [])

            if len(extra_images) > 5:
                # raise ValueError(f"Too many images ({len(extra_images)}) for merchant_sku='{merchant_sku}'!")
                # OR just keep the first 5 & warn:
                print(f"ERROR: merchant_sku='{merchant_sku}' has {len(extra_images)} images in images.csv; " 
                      f"keeping only first 5. (row {row_index})")
                extra_images = extra_images[:5]

            for url in extra_images:
                item_doc["images"].append({
                    "hash": "",
                    "url": url
                })
            
            if item_doc["images"]:
                first_img = item_doc["images"][0]

                item_doc["image"] = first_img.get("url", "")  # main image url
                item_doc["image_blur"] = first_img.get("hash", "")  # or some placeholder
            else:
                pass

            # link item to the correct option if 'merchant_sku' is present
            merchant_sku = row.get("merchant_sku", "").strip()
            if merchant_sku and merchant_sku in externalid_to_option:
                matched_option = externalid_to_option[merchant_sku]
                link_id = generate_random_id()
                option_reference = {
                    "id": {"_id": link_id},
                    "name": [],
                    "option_id": matched_option["$oid"],
                    "prerequisite_values": []
                }
                item_doc["options"].append(option_reference)
            if sub_cat_str:
                if (cat_name_str, sub_cat_str) in cat_map:
                    cat_map[(cat_name_str, sub_cat_str)]["items"].append({
                        "id": {"_id": generate_random_id()},
                        "item_id": {"_id": item_id}
                    })
                else:
                    fallback_key = (cat_name_str, "Misc")
                    if fallback_key in cat_map:
                        cat_map[fallback_key]["items"].append({
                            "id": {"_id": generate_random_id()},
                            "item_id": {"_id": item_id}
                        })
                    else:
                        print(f"⚠️ WARNING: (cat_name='{cat_name_str}',sub_cat='{sub_cat_str}') not found. No 'Misc' fallback.")
            else:
                fallback_key = (cat_name_str, "Misc")
                if fallback_key in cat_map:
                    cat_map[fallback_key]["items"].append({
                        "id": {"_id": generate_random_id()},
                        "item_id": {"_id": item_id}
                    })
                else:
                    leaf_key = (cat_name_str, "")
                    if leaf_key in cat_map:
                        parent_cat = cat_map[leaf_key]
                        if parent_cat.get("child_category_ids"):
                            print(f"⚠️ WARNING: Parent cat '{cat_name_str}' has subcats. '{item_id}' not assigned.")
                        else:
                            parent_cat["items"].append({
                                "id": {"_id": generate_random_id()},
                                "item_id": {"_id": item_id}
                            })
                    else:
                        print(f"❌ ERROR: No matching cat for (cat_name='{cat_name_str}', sub_cat='') => not attached.")

            items.append(item_doc)

    return items

def strip_images(json_data):
    """
    Recursively remove or neutralize all image fields:
      - If 'image_blur' or 'hash' is found, delete it.
      - If 'image' is found, set it to "" (empty string).
      - If 'images' is found, set it to [] (empty list).
    Works on both categories (which typically have 'image', 'image_blur')
    and items (which may have 'image', 'images', 'image_blur'), etc.
    """

    if isinstance(json_data, dict):
        if "image_blur" in json_data:
            del json_data["image_blur"]
        if "hash" in json_data:
            del json_data["hash"]
        if "image" in json_data:
            del json_data["image"]
        if "images" in json_data:
            json_data["images"] = []
        for key, value in list(json_data.items()):
            json_data[key] = strip_images(value)

    elif isinstance(json_data, list):
        return [strip_images(item) for item in json_data]
    return json_data


def remove_images_in_json_file(input_path, output_path):
    """
    Reads a JSON file, runs 'strip_images' to remove all
    references to images, then writes the cleaned JSON.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = strip_images(data)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"✅ Cleaned JSON saved to {output_path}")

def move_parent_items_to_misc(cata_obj):
    """
    After the catalog is built, some parent categories (with subcategories) may still have 'items'.
    This function scans them, finds their 'Misc' subcategory, and moves all items there.
    
    If no 'Misc' subcategory is found, it logs a warning and leaves them.
    Returns the modified cata_obj for convenience.
    """
    
    if "categories" not in cata_obj:
        print("WARNING: No 'categories' found with something something in cata_obj. do nothing.")
        return cata_obj
    cat_lookup = {}
    for cat in cata_obj["categories"]:
        cat_id = cat["id"]["_id"]
        cat_lookup[cat_id] = cat
    for cat in cata_obj["categories"]:
        cat_id = cat["id"]["_id"]
        cat_name = cat["name"][0]["value"] if cat.get("name") else "Unknown"
        print(f"\n[DEBUG] Checking category since it has something something while '{cat_name}' (ID={cat_id})")
        print(f"        child_category_ids={cat.get('child_category_ids', [])}")
        print(f"        items={cat.get('items', [])}")

        if cat.get("child_category_ids") and cat.get("items"):
            items_to_move = cat["items"]
            misc_cat = None
            for child_id_obj in cat["child_category_ids"]:
                child_id = child_id_obj["_id"]
                child_cat = cat_lookup[child_id]
                child_name = child_cat["name"][0]["value"].strip().lower()
                if child_name == "misc":
                    misc_cat = child_cat
                    break
            if misc_cat:
                print(f"[DEBUG]  --> FOUND 'Misc' subcat for '{cat_name}' (ID={cat_id}). Moving {len(items_to_move)} items now...")
                misc_cat["items"].extend(items_to_move)
                cat["items"] = []
                print(f"[DEBUG]  --> DONE: Moved items to 'Misc'. Parent now has items={cat['items']}")
            else:
                print(f"⚠️ WARNING: Parent category '{cat_name}' ({cat_id}) has subcategories "
                      f"but no 'Misc' child found. Items remain here = {len(items_to_move)}")

    return cata_obj

def check_for_parent_items(catalog):

    found_issues = False 
    for cat in catalog["categories"]:
        cat_name = cat["name"][0]["value"] if cat.get("name") else "Unknown"
        cat_id = cat["id"]["_id"]
        child_ids = cat.get("child_category_ids", [])
        items = cat.get("items", [])

        if child_ids:
            if items:
                print(f"🚨 PARENT CATEGORY '{cat_name}' ({cat_id}) still has {len(items)} items!")
                found_issues = True
            else:
                print(f"✅ Parent category '{cat_name}' ({cat_id}) has no items. (Correct)")
        else:
            print(f"✅ Leaf category '{cat_name}' ({cat_id}) is allowed to have items.")

    if not found_issues:
        print("🎉 SUCCESS: No parent categories contain items!")

def parse_images_csv(images_csv_path):
    """
    Reads images.csv, which has exactly 2 columns:
      merchant_sku, image_url
    Returns a dict: merchant_sku -> list of image_urls (in the same order).
    """
    import csv
    from collections import defaultdict
    sku_to_images = defaultdict(list)

    with open(images_csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        required_cols = ["merchant_sku", "image_url"]
        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"ERROR: images.csv must have a has something something '{col}'.")

        for row in reader:
            merchant_sku = row["merchant_sku"].strip()
            image_url = row["image_url"].strip()
            
            if not merchant_sku or not image_url:
                print(f"Warning: row with empty has something something merchant_sku='{merchant_sku}' or image_url='{image_url}'. Skipping.")
                continue

            sku_to_images[merchant_sku].append(image_url)

    return sku_to_images

def force_no_images(json_data):
    """
    Recursively sets:
      "image" => "",
      "image_blur" => "",
      "images" => []
    in all dictionaries/lists of the final JSON.
    """
    if isinstance(json_data, dict):
        if "image" in json_data:
            json_data["image"] = ""
        if "image_blur" in json_data:
            json_data["image_blur"] = ""
        if "images" in json_data:
            json_data["images"] = []

        for key, value in json_data.items():
            json_data[key] = force_no_images(value)

    elif isinstance(json_data, list):
        return [force_no_images(item) for item in json_data]

    return json_data

def assign_category_images(cata_obj, items_list):
    """
    For each category in cata_obj['categories'],
    find the "first" item (BFS or DFS),
    copy that item’s first image => category.image (and set image_blur="").
    """
    item_map = {}
    for it in items_list:
        it_id = it["$oid"]["_id"]
        item_map[it_id] = it
    cat_lookup = {}
    for cat in cata_obj["categories"]:
        cid = cat["id"]["_id"]
        cat_lookup[cid] = cat
    def find_first_item_id(cat_id):
        cat_obj = cat_lookup[cat_id]
        if "items" in cat_obj and cat_obj["items"]:
            return cat_obj["items"][0]["item_id"]["_id"]
        for child_cat_id_obj in cat_obj.get("child_category_ids", []):
            child_id = child_cat_id_obj["_id"]
            found = find_first_item_id(child_id)
            if found:
                return found
        return None  # no items found

    for cat in cata_obj["categories"]:
        cat_id = cat["id"]["_id"]
        item_id = find_first_item_id(cat_id)
        if item_id and item_id in item_map:
            item_doc = item_map[item_id]
            if item_doc.get("images"):
                cat["image"] = item_doc["images"][0].get("url", "")
                cat["image_blur"] = ""
            else:
                cat["image"] = item_doc.get("image", "")
                cat["image_blur"] = ""
        else:
            cat["image"] = ""
            cat["image_blur"] = ""

    print("✅ Done assigning category images from the first item found.")

def main(items_csv, options_csv, images_csv, output_json):

    cata_obj, cat_map = cats_gen(items_csv)
    cata_id = cata_obj["$oid"]["_id"]
    options_list = opts_gen(options_csv, cata_id)
    sku_to_images = parse_images_csv(images_csv)
    items_list = items_gen(items_csv, cata_id, options_list, cat_map, sku_to_images)
    cata_obj = assign_category_images(cata_obj)
    move_parent_items_to_misc(cata_obj, items_list)
    check_for_parent_items(cata_obj)

    final_json = {
        "items": items_list,
        "catalog": cata_obj,
        "options": options_list
    }

    # (OPTIONALLY) if you do not want to remove images, do not call force_no_images
    # instead, if you do want to force-remove or empty them => skip or do remove_images_in_json_file if you want.

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)

    print(f"✅ Final JSON => {output_json}")

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "data")

    items_csv = os.path.join(base_dir, "items.csv")
    options_csv = os.path.join(base_dir, "options.csv")
    images_csv = os.path.join(base_dir, "images.csv")

    # You can change the venue name to customize the output filename
    venue = "demo_catalog"
    output_json = os.path.join(base_dir, f"{venue}.json")

    # final main() to generate the json
    main(items_csv, options_csv, images_csv, output_json)
