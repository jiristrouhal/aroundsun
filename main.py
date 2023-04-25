import around_sun
import es_jiri_profiler.profiling


@es_jiri_profiler.profiling.profile
def main():
	around_sun.main()

main()
