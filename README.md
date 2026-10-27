# Streaming Cost Anomaly Detector

## Overview

Due to poor CPU sizing, streaming platforms waste money in Kubernetes when their containers are over-provisioned or risk performance when containers are under-provisioned. It goes unnoticed because nothing alerts on waste, only failures. This tool pulls CPU metrics from Prometheus and classifies each container's CPU sizing using fixed rules, while Claude explains each result in plain English. The output is an HTML report with a facts table plus a short explanation per container which the SRE team can scan in under a minute.

## Sample Output

![alt text](sample-report_2026-10-25_00-35.png)

`checkout-api` is over-provisioned, `recommendation-engine` is bursty and `video-transcoder` is right-sized. My code builds the table and decides the labels, and Claude only writes the explanations from labels, reasons, and restart warnings.

## How It Works



## Tech Stack


## How To Run It


## Key Decisions



## What I'd Do Differently/Next 