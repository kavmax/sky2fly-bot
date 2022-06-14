import cv2
import numpy as np


def add_hsv_mask(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    color_mask = cv2.inRange(
        hsv_frame, lowerb=np.array([60, 225, 0]), upperb=np.array([65, 255, 255]))
    return cv2.bitwise_and(hsv_frame, hsv_frame, mask=color_mask)


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, -angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def scale_image(image, percent, maxwh):
    max_width = maxwh[1]
    max_height = maxwh[0]
    max_percent_width = max_width / image.shape[1] * 100
    max_percent_height = max_height / image.shape[0] * 100
    if max_percent_width < max_percent_height:
        max_percent = max_percent_width
    else:
        max_percent = max_percent_height
    if percent > max_percent:
        percent = max_percent
    width = int(image.shape[1] * percent / 100)
    height = int(image.shape[0] * percent / 100)
    result = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    return result, percent


def modified_match_template(rgbimage, rgbtemplate, method, matched_thresh, rgbdiff_thresh, rot_range, rot_interval, scale_range, scale_interval, rm_redundant, minmax):
    """
    rgbimage: RGB image where the search is running.
    rgbtemplate: RGB searched template. It must be not greater than the source image and have the same data type.
    method: [String] Parameter specifying the comparison method
    matched_thresh: [Float] Setting threshold of matched results(0~1).
    rgbdiff_thresh: [Float] Setting threshold of average RGB difference between template and source image.
    rot_range: [Integer] Array of range of rotation angle in degrees. Example: [0,360]
    rot_interval: [Integer] Interval of traversing the range of rotation angle in degrees.
    scale_range: [Integer] Array of range of scaling in percentage. Example: [50,200]
    scale_interval: [Integer] Interval of traversing the range of scaling in percentage.
    rm_redundant: [Boolean] Option for removing redundant matched results based on the width and height of the template.
    minmax:[Boolean] Option for finding points with minimum/maximum value.
    Returns: List of satisfied matched points in format [[point.x, point.y], angle, scale].
    """
    image_maxwh = rgbimage.shape
    height, width, numchannel = rgbtemplate.shape
    all_points = []
    if minmax == False:
        for next_angle in range(rot_range[0], rot_range[1], rot_interval):
            for next_scale in range(scale_range[0], scale_range[1], scale_interval):
                scaled_template, actual_scale = scale_image(rgbtemplate, next_scale, image_maxwh)
                if next_angle == 0:
                    rotated_template = scaled_template
                else:
                    rotated_template = rotate_image(scaled_template, next_angle)
                if method == "TM_CCOEFF":
                    matched_points = cv2.matchTemplate(rgbimage, rotated_template,cv2.TM_CCOEFF)
                    satisfied_points = np.where(matched_points >= matched_thresh)
                elif method == "TM_CCOEFF_NORMED":
                    matched_points = cv2.matchTemplate(rgbimage, rotated_template,cv2.TM_CCOEFF_NORMED)
                    satisfied_points = np.where(matched_points >= matched_thresh)
                elif method == "TM_CCORR":
                    matched_points = cv2.matchTemplate(rgbimage, rotated_template,cv2.TM_CCORR)
                    satisfied_points = np.where(matched_points >= matched_thresh)
                elif method == "TM_CCORR_NORMED":
                    matched_points = cv2.matchTemplate(rgbimage, rotated_template,cv2.TM_CCORR_NORMED)
                    satisfied_points = np.where(matched_points >= matched_thresh)
                elif method == "TM_SQDIFF":
                    matched_points = cv2.matchTemplate(rgbimage, rotated_template,cv2.TM_SQDIFF)
                    satisfied_points = np.where(matched_points <= matched_thresh)
                elif method == "TM_SQDIFF_NORMED":
                    matched_points = cv2.matchTemplate(rgbimage, rotated_template,cv2.TM_SQDIFF_NORMED)
                    satisfied_points = np.where(matched_points <= matched_thresh)
                # else:
                #     raise MethodError("There's no such comparison method for template matching.")
                for pt in zip(*satisfied_points[::-1]):
                    all_points.append([pt, next_angle, actual_scale])
    else:
        for next_angle in range(rot_range[0], rot_range[1], rot_interval):
            for next_scale in range(scale_range[0], scale_range[1], scale_interval):
                scaled_template, actual_scale = scale_image(rgbtemplate, next_scale, image_maxwh)
                if next_angle == 0:
                    rotated_template = scaled_template
                else:
                    rotated_template = rotate_image(scaled_template, next_angle)
                if method == "TM_CCOEFF":
                    matched_points = cv2.matchTemplate(rgbimage,rotated_template,cv2.TM_CCOEFF)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matched_points)
                    if max_val >= matched_thresh:
                        all_points.append([max_loc, next_angle, actual_scale, max_val])
                elif method == "TM_CCOEFF_NORMED":
                    matched_points = cv2.matchTemplate(rgbimage,rotated_template,cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matched_points)
                    if max_val >= matched_thresh:
                        all_points.append([max_loc, next_angle, actual_scale, max_val])
                elif method == "TM_CCORR":
                    matched_points = cv2.matchTemplate(rgbimage,rotated_template,cv2.TM_CCORR)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matched_points)
                    if max_val >= matched_thresh:
                        all_points.append([max_loc, next_angle, actual_scale, max_val])
                elif method == "TM_CCORR_NORMED":
                    matched_points = cv2.matchTemplate(rgbimage,rotated_template,cv2.TM_CCORR_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matched_points)
                    if max_val >= matched_thresh:
                        all_points.append([max_loc, next_angle, actual_scale, max_val])
                elif method == "TM_SQDIFF":
                    matched_points = cv2.matchTemplate(rgbimage,rotated_template,cv2.TM_SQDIFF)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matched_points)
                    if min_val <= matched_thresh:
                        all_points.append([min_loc, next_angle, actual_scale, min_val])
                elif method == "TM_SQDIFF_NORMED":
                    matched_points = cv2.matchTemplate(rgbimage,rotated_template,cv2.TM_SQDIFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matched_points)
                    if min_val <= matched_thresh:
                        all_points.append([min_loc, next_angle, actual_scale, min_val])
                # else:
                #     raise MethodError("There's no such comparison method for template matching.")
        if method == "TM_CCOEFF":
            all_points = sorted(all_points, key=lambda x: -x[3])
        elif method == "TM_CCOEFF_NORMED":
            all_points = sorted(all_points, key=lambda x: -x[3])
        elif method == "TM_CCORR":
            all_points = sorted(all_points, key=lambda x: -x[3])
        elif method == "TM_CCORR_NORMED":
            all_points = sorted(all_points, key=lambda x: -x[3])
        elif method == "TM_SQDIFF":
            all_points = sorted(all_points, key=lambda x: x[3])
        elif method == "TM_SQDIFF_NORMED":
            all_points = sorted(all_points, key=lambda x: x[3])
    if rm_redundant == True:
        lone_points_list = []
        visited_points_list = []
        for point_info in all_points:
            point = point_info[0]
            scale = point_info[2]
            all_visited_points_not_close = True
            if len(visited_points_list) != 0:
                for visited_point in visited_points_list:
                    if ((abs(visited_point[0] - point[0]) < (width * scale / 100)) and (abs(visited_point[1] - point[1]) < (height * scale / 100))):
                        all_visited_points_not_close = False
                if all_visited_points_not_close == True:
                    lone_points_list.append(point_info)
                    visited_points_list.append(point)
            else:
                lone_points_list.append(point_info)
                visited_points_list.append(point)
        points_list = lone_points_list
    else:
        points_list = all_points
    return points_list
