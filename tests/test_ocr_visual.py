import os
import json
import pytest

def get_all_json_outputs(output_dir):
    return [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('_ocr.json')]

def load_ocr_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def check_json_structure(ocr_json):
    assert 'pdf_file' in ocr_json
    assert 'pages' in ocr_json
    assert isinstance(ocr_json['pages'], list)
    for page in ocr_json['pages']:
        assert 'page_number' in page
        assert 'text' in page
        assert 'regions' in page
        assert 'visualization_path' in page
        assert isinstance(page['regions'], list)
        for region in page['regions']:
            assert 'bbox' in region
            assert 'text' in region
            assert 'conf' in region
            assert isinstance(region['bbox'], list)
            assert len(region['bbox']) == 4
            assert isinstance(region['text'], str)
            assert isinstance(region['conf'], int)

def check_page_text_not_empty(ocr_json):
    for page in ocr_json['pages']:
        if not page['text'].strip():
            print(f"Warning: Page {page['page_number']} in {ocr_json['pdf_file']} has empty OCR text.")

def check_visualization_file_exists(ocr_json):
    for page in ocr_json['pages']:
        assert os.path.exists(page['visualization_path']), f"Missing visualization: {page['visualization_path']}"

def check_confidence_range(ocr_json):
    for page in ocr_json['pages']:
        for region in page['regions']:
            assert 0 <= region['conf'] <= 100, f"Confidence out of range: {region['conf']}"

def check_bbox_validity(ocr_json):
    for page in ocr_json['pages']:
        for region in page['regions']:
            x1, y1, x2, y2 = region['bbox']
            assert x2 > x1 and y2 > y1, f"Invalid bbox: {region['bbox']}"

def check_filename_consistency(ocr_json):
    # The base name of the PDF file should match the JSON file name (ignoring _ocr.json suffix)
    pdf_basename = os.path.splitext(os.path.basename(ocr_json['pdf_file']))[0]
    json_basename = os.path.basename(ocr_json['pdf_file']).replace('.pdf','')
    assert pdf_basename in ocr_json['pdf_file'], f"PDF filename mismatch: {ocr_json['pdf_file']}"

def check_high_confidence_region(ocr_json, min_conf=70):
    for page in ocr_json['pages']:
        high_conf = [r for r in page['regions'] if r['conf'] >= min_conf]
        assert high_conf, f"No high-confidence region on page {page['page_number']} in {ocr_json['pdf_file']}"

def check_no_duplicate_bboxes(ocr_json):
    for page in ocr_json['pages']:
        seen = set()
        for region in page['regions']:
            bbox_tuple = tuple(region['bbox'])
            assert bbox_tuple not in seen, f"Duplicate bbox {bbox_tuple} on page {page['page_number']} in {ocr_json['pdf_file']}"
            seen.add(bbox_tuple)

def check_regions_sorted(ocr_json):
    for page in ocr_json['pages']:
        bboxes = [region['bbox'] for region in page['regions']]
        # Sort by y1, then x1 (top-to-bottom, then left-to-right)
        sorted_bboxes = sorted(bboxes, key=lambda b: (b[1], b[0]))
        assert bboxes == sorted_bboxes, f"Regions not sorted top-to-bottom, left-to-right on page {page['page_number']} in {ocr_json['pdf_file']}"

def test_all_ocr_outputs():
    output_dir = 'ocr_visualization_output'
    all_jsons = get_all_json_outputs(output_dir)
    assert all_jsons, "No OCR JSON outputs found. Run ocr_visual.py first."
    for path in all_jsons:
        ocr_json = load_ocr_json(path)
        check_json_structure(ocr_json)
        check_page_text_not_empty(ocr_json)
        check_visualization_file_exists(ocr_json)
        check_confidence_range(ocr_json)
        check_bbox_validity(ocr_json)
        check_filename_consistency(ocr_json)
        check_high_confidence_region(ocr_json)
        check_no_duplicate_bboxes(ocr_json)
        check_regions_sorted(ocr_json)
