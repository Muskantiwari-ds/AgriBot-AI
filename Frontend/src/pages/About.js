import React from "react";

function About() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">About AgriSense</h1>
      <p className="mb-2">
        AgriSense is an AI-powered advisor designed to assist farmers, vendors,
        and financiers with crop, weather, finance, and policy-related queries.
      </p>
      <p>
        The platform uses public datasets, retrieval-augmented generation, and
        multilingual support to provide reliable and explainable insights even
        in low-connectivity environments.
      </p>
    </div>
  );
}

export default About;
