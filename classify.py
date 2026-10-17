def classify(peak, avg, restarts):
    if peak > 1.0:
        label = "under-provisioned"
        reason = f"Peak CPU usage of {peak*100:.2f}% exceeds requested resources"
    elif peak < 0.3:
        label = "over-provisioned"
        reason = f"Peak CPU usage of {peak*100:.2f}% is significantly below requested resources"
    elif avg == 0.0:
        label = "insufficient-data"
        reason = f"The numbers don\'t make sense: Peak CPU usage is {peak*100:.2f}% and average CPU usage is {avg*100:.2f}% of requested resources"
    elif peak/avg > 1.5:
        label = "bursty"
        reason = f"Peak and average ratio {peak/avg:.2f} with peak usage of {peak*100:.2f}% and average usage of {avg*100:.2f}% indicates spikes in resource usage and cost inefficiency"
    else:
        label = "right-sized"
        reason = f"Peak CPU usage is {peak*100:.2f}% and average CPU usage is {avg*100:.2f}% of requested resources indicating efficient resource usage"
    warning = None
    if restarts > 5:
        warning = f'{restarts:.0f} restarts in the last 7 days'
    result = {"label": label, "reason": reason, "warning": warning}
    return result


if __name__ == "__main__":
    cases = [
        (1.2, 0.5, 301.7, "under-provisioned"),
        (0.0, 0.0, 301.7, "over-provisioned"),
        (1.0, 0.9, 301.7, "right-sized"),
        (0.3, 0.0, 301.7, "insufficient-data"),
        (0.99, 0.41, 301.7, "bursty"),
        (0.99, 0.66, 301.7, "right-sized"),
        (0.99, 0.66, 5.0, "right-sized"),
        (0.99, 0.66, 0.0, "right-sized"),
    ]
    for peak, avg, restarts, expected in cases:
        classification = classify(peak, avg, restarts)
        print(f"Status: {status}, Label: {classification['label']}, Reason: {classification['reason']}, Warning: {classification['warning']}")