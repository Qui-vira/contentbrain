"use client";

import React from "react";

interface MarqueeProps {
  items: string[];
  speed?: number;
  separator?: string;
  className?: string;
  renderItem?: (item: string, index: number) => React.ReactNode;
}

export function Marquee({
  items,
  speed = 30,
  separator = " / ",
  className = "",
  renderItem,
}: MarqueeProps) {
  if (renderItem) {
    // Custom render mode — render each item with the callback
    const itemElements = items.map((item, i) => (
      <React.Fragment key={i}>{renderItem(item, i)}</React.Fragment>
    ));
    return (
      <div className={`overflow-hidden whitespace-nowrap ${className}`}>
        <div
          className="inline-flex animate-marquee items-center"
          style={{ animationDuration: `${speed}s` }}
        >
          {itemElements}
          {itemElements}
          {itemElements}
        </div>
      </div>
    );
  }

  const content = items.join(separator) + separator;

  return (
    <div className={`overflow-hidden whitespace-nowrap ${className}`}>
      <div
        className="inline-flex animate-marquee"
        style={{
          animationDuration: `${speed}s`,
        }}
      >
        <span className="inline-block pr-4">{content}</span>
        <span className="inline-block pr-4">{content}</span>
        <span className="inline-block pr-4">{content}</span>
      </div>
    </div>
  );
}
