from coviso.sim import Simulator


def main() -> None:
    sim = Simulator((1280, 720))

    config_path = "config/zone_config.json"

    sim.add_task_config("Test", config_path)

    sim.run()


if __name__ == "__main__":
    main()
