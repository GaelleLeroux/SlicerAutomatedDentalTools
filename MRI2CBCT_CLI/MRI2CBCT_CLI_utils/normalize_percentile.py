import argparse
import os
import SimpleITK as sitk
import numpy as np

def compute_thresholds(image, lower_percentile=10, upper_percentile=90):
    """
    Computes intensity thresholds for an image based on specified percentiles.

    Arguments:
    image (SimpleITK.Image): The input image.
    lower_percentile (float): The lower percentile for threshold computation (default is 10).
    upper_percentile (float): The upper percentile for threshold computation (default is 90).
    """
    array = sitk.GetArrayFromImage(image)
    lower_threshold = np.percentile(array, lower_percentile)
    upper_threshold = np.percentile(array, upper_percentile)
    return lower_threshold, upper_threshold

def enhance_contrast(image,upper_percentile,lower_percentile, min_norm, max_norm):
    """
    Enhances the contrast of the image while normalizing its intensity values.

    Arguments:
    image (SimpleITK.Image): The input image.
    upper_percentile (float): The upper percentile for threshold computation.
    lower_percentile (float): The lower percentile for threshold computation.
    min_norm (float): The minimum normalization value.
    max_norm (float): The maximum normalization value.
    """
    # Compute thresholds
    lower_threshold, upper_threshold = compute_thresholds(image,lower_percentile,upper_percentile)


    # Normalize the image using the computed thresholds
    array = sitk.GetArrayFromImage(image)
    normalized_array = np.clip((array - lower_threshold) / (upper_threshold - lower_threshold), 0, 1)
    scaled_array = normalized_array * max_norm - min_norm
    
    return sitk.GetImageFromArray(scaled_array)

def normalize(input_folder, output_folder,upper_percentile,lower_percentile,min_norm, max_norm):
    """
    Processes and normalizes all .nii.gz images in the input folder, enhancing their contrast.

    Arguments:
    input_folder (str): Path to the folder containing the input images.
    output_folder (str): Path to the folder to save the normalized images.
    upper_percentile (float): Upper percentile for threshold computation.
    lower_percentile (float): Lower percentile for threshold computation.
    min_norm (float): Minimum normalization value.
    max_norm (float): Maximum normalization value.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.nii.gz'):
            input_path = os.path.join(input_folder, filename)
            img = sitk.ReadImage(input_path)
            
            # Enhance the contrast of the image
            enhanced_img = enhance_contrast(img,upper_percentile,lower_percentile,min_norm, max_norm)
            
            # Copy original metadata to the enhanced image
            enhanced_img.CopyInformation(img)
            
            # Save the enhanced image with the new suffix
            output_filename = filename.replace('.nii.gz', f'_percentile=[{lower_percentile},{upper_percentile}]_norm=[{min_norm},{max_norm}].nii.gz')
            output_path = os.path.join(output_folder, output_filename)
            sitk.WriteImage(enhanced_img, output_path)
            print(f'Saved enhanced image to {output_path}')

def main():
    parser = argparse.ArgumentParser(description='Enhance contrast of NIfTI images and save with a new suffix.')
    parser.add_argument('--input_folder', type=str, help='Path to the input folder containing .nii.gz images.', default="/home/lucia/Documents/Gaelle/Data/MultimodelReg/Segmentation/a3_Registration_closer_all/b0_CBCT")
    parser.add_argument('--output_folder', type=str, help='Path to the output folder to save normalized images.', default="/home/lucia/Documents/Gaelle/Data/MultimodelReg/Segmentation/a3_Registration_closer_all/b2_CBCT_norm")
    parser.add_argument('--upper_percentile', type=int, help='upper percentile to apply, choose between 0 and 100',default=95)
    parser.add_argument('--lower_percentile', type=int, help='lower percentile to apply, choose between 0 and 100',default=10)
    parser.add_argument('--max_norm', type=int, help='max value after normalization',default=75)
    parser.add_argument('--min_norm', type=int, help='min value after normalization',default=0)
    
    args = parser.parse_args()
    
    output_path = os.path.join(args.output_folder,f"test_percentile=[{args.lower_percentile},{args.upper_percentile}]_norm=[{args.min_norm},{args.max_norm}]")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    normalize(args.input_folder, output_path, args.upper_percentile,args.lower_percentile,args.min_norm, args.max_norm)

if __name__ == '__main__':
    main()
