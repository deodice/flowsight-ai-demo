"use client";

import { useEffect, useState } from "react";

function formatToday() {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric"
  }).format(new Date()).toUpperCase();
}

export function CurrentDateLabel() {
  const [label, setLabel] = useState(formatToday);

  useEffect(() => {
    setLabel(formatToday());
  }, []);

  return <>{label}</>;
}
