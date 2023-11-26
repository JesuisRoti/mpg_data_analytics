import Link from 'next/link';
import styles from '@/app/components/layout.module.css';

export default function Home() {
    return (
      <main className={styles.container}>
        <div>Welcome to the MPG DATA ANALYSIS project !</div>
		  <div>Here is the important page : <Link href="/front-mpg">About Us</Link></div>
      </main>
    )
}
