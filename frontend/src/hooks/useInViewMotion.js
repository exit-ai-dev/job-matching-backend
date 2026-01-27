import { useEffect, useRef, useState } from 'react';

export const useInViewMotion = (options = { threshold: 0.2 }) => {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: options.threshold ?? 0.2 }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [options.threshold]);

  return { ref, visible };
};
