import Chart from "@/app/components/chart";
import styles from '@/app/components/layout.module.css';

export default function Home() {
    return (
      <main className={styles.container}>
        <Chart />
      </main>
    )
}
