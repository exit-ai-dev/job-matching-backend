import { useEffect, useRef, useState } from 'react';

export const useScrollDirection = (threshold = 6, offset = 80) => {
  const [show, setShow] = useState(true);
  const last = useRef(0);

  useEffect(() => {
    const onScroll = () => {
      const current = window.scrollY;
      const delta = current - last.current;
      if (Math.abs(delta) < threshold) return;
      const hide = current > offset && delta > 0;
      setShow(!hide);
      last.current = current;
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, [threshold, offset]);

  return show;
};
